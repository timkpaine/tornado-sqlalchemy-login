import ujson
import tornado.web
import tornado.escape
import tornado.gen
from tornado.concurrent import run_on_executor
from .base import AuthenticatedHandler


class APIKeyHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        yield self._get()

    @run_on_executor
    def _get(self):
        self.write(self.apikeys())

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        yield self._post()

    @run_on_executor
    def _post(self):
        user = self.get_user()
        if not user:
            self._set_400("User malformed")
        ret = self.delete_apikey(self.get_argument("id")) if self.get_argument("id", "") else self.new_apikey()
        if ret:
            self.finish(ret)
        else:
            self._set_401("Unauthorized to delete/modify key")
