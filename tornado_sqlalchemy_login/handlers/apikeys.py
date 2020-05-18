import tornado.web
import tornado.escape
import tornado.gen
from .base import AuthenticatedHandler


class APIKeyHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self):
        self.write(self.apikeys())

    @tornado.web.authenticated
    def post(self):
        user = self.get_user()
        if not user:
            self._set_400("User malformed")
        ret = self.delete_apikey(self.get_argument("id")) if self.get_argument("id", "") else self.new_apikey()
        if ret:
            self.finish(ret)
        else:
            self._set_401("Unauthorized to delete/modify key")
