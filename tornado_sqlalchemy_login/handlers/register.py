import tornado.gen
import tornado.escape
import tornado.web
import ujson
from tornado.concurrent import run_on_executor
from .base import ServerHandler


class RegisterHandler(ServerHandler):
    def on_register(self, user):
        pass

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        '''Get the current list of users ids'''
        yield self._get()

    @run_on_executor
    def _get(self):
        if self.current_user and int(self.current_user) not in self._users:
            return self.post()
        if self.is_admin:
            with self.session() as session:
                self.write(ujson.dumps(session.query(self.user_sql_class).all()))
        else:
            self._set_401("Unauthorized to view all users")

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


class APIKeyHandler(ServerHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        yield self._get()

    @run_on_executor
    def _get(self):
        with self.session() as session:
            user = session.query(self.user_sql_class).filter_by(**{self.user_id_field: int(self.current_user)}).first()
            if not user:
                self._set_400("User malformed")
            self.write({getattr(a, self.apikey_id_field): a.to_dict() for a in getattr(user, self.user_apikeys_field)})

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
