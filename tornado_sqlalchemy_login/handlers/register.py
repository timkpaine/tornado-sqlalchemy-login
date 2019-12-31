import ujson
import tornado.web
import tornado.escape
import tornado.gen
from tornado.concurrent import run_on_executor
from .base import AuthenticatedHandler


class RegisterHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        yield self._get()

    @run_on_executor
    def _get(self):
        if self.current_user:
            self.redirect('api/v1/register')
        else:
            self.redirect_home()

    @tornado.gen.coroutine
    def post(self):
        '''Register a user. user will be assigned a session id'''
        yield self._post()

    @run_on_executor
    def _post(self):
        try:
            body = tornado.escape.json_decode(self.request.body or '{}')
        except ValueError:
            body = {}
        username = self.get_argument('username', body.get('username', ''))
        email = self.get_argument('email', body.get('email', ''))
        password = self.get_argument('password', body.get('password', ''))

        if not username or not email or not password:
            self._set_400("User malformed")

        with self.session() as session:
            c = self.user_sql_class(username=username, email=email, password=password)

            try:
                session.add(c)
                session.commit()
                session.refresh(c)
                ret = self._login_post(c)

                self.on_register(c)
                self._writeout(ujson.dumps(ret), "Registering user {}", ret[self.user_id_field])
                return
            except BaseException:
                self._set_400("User malformed")
                return
