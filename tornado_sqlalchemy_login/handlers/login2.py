import ujson
import tornado.web
import tornado.escape
import tornado.gen
from tornado.concurrent import run_on_executor
from .base2 import AuthenticatedHandler


class LoginHandler(AuthenticatedHandler):
    def get(self):
        if self.current_user:
            self.redirect('api/v1/register')
        else:
            self.redirect_home()

    def post(self):
        # Get from current user
        user = self.get_user()
        # Get from username/password
        if not user:
            user = self.get_user_from_username_password()
        # get from apikey/secret
        if not user:
            user = self.get_user_from_key()
        if user:
            # return data in json
            self.finish(self.login(user))
            return
        # set 401
        self._set_401("User not recognized")


class LogoutHandler(AuthenticatedHandler):
    def get(self):
        self.logout()
        self.redirect_home()

    def post(self):
        self.logout()


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


class APIKeyHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        yield self._get()

    @run_on_executor
    def _get(self):
        self.write(self.get_apikeys_for_user(self.get_current_user()))

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        yield self._post()

    @run_on_executor
    def _post(self):
        with self.session() as session:
            user = session.query(self.user_sql_class).filter_by(**{self.user_id_field: int(self.current_user)}).first()
            if not user:
                self._set_400("User malformed")
            if self.get_argument("id", ""):
                # delete key
                key = session.query(self.apikey_sql_class).filter_by(**{self.apikey_id_field: int(self.get_argument("id"))}).first()
                if getattr(key, self.apikey_user_field) == user:
                    session.delete(key)
                else:
                    self._set_401("Unauthorized to delete key")
            else:
                # new key
                apikey = self.apikey_sql_class(**{self.apikey_user_field: user})
                session.add(apikey)
