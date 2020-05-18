import tornado.web
import tornado.escape
import tornado.gen
from .base import AuthenticatedHandler


class RegisterHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self):
        if self.current_user:
            self.redirect('api/v1/register')
        else:
            self.redirect_home()

    def post(self):
        '''Register a user. user will be assigned a session id'''
        self.finish(self.register())
