import tornado.gen
from tornado.concurrent import run_on_executor
from .base import ServerHandler
from ..web import parse_body


class LoginHandler(ServerHandler):
    def on_login(self, user):
        pass

    @tornado.gen.coroutine
    def get(self):
        '''Get the login page'''
        yield self._get()

    @run_on_executor
    def _get(self):
        if self.current_user:
            self.redirect('api/v1/register')
        else:
            self.redirect(self.basepath + "home")

    @tornado.gen.coroutine
    def post(self):
        '''Login'''
        if self.current_user:
            user_id = self.current_user
            with self.session() as session:
                user = session.query(self.user_sql_class).filter_by(**{self.user_id_field: user_id}).first()
                if user:
                    self.login(user)
                    self.on_login(user)
                    return
        body = parse_body(self.request)
        username = self.get_argument('username', body.get('username', ''))
        password = self.get_argument('password', body.get('password', ''))

        if not username or not password:
            user_id = self.get_user_from_key()
            if not user_id:
                self._set_400("User not registered")
            return

        if not self.get_user_from_username_password():
            self._set_400("User not registered")


class LogoutHandler(ServerHandler):
    def on_logout(self, user):
        pass

    def get(self):
        '''clear cookie'''
        self.on_logout(self.current_user)
        self.clear_cookie("user")
        self.redirect(self.basepath + "home")

    def post(self):
        '''Get the logout page'''
        self.clear_cookie("user")
