import tornado.web
import os.path
import tornado_sqlalchemy_login
from tornado_sqlalchemy_login.handlers import HTMLHandler, HTMLOpenHandler
from mock import MagicMock
from tornado.web import HTTPError

context = {'users': {},
           'sessionmaker': MagicMock()}


class TestHTML:
    def setup(self):
        settings = {
            "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url": "/login",
            "debug": "True",
            "template_path": os.path.join(os.path.dirname(tornado_sqlalchemy_login.__file__), 'assets', 'templates'),
        }
        self.app = tornado.web.Application(**settings)
        self.app._transforms = []

    def test_HTMLOpenHandler(self):
        req = MagicMock()
        req.body = ''
        x = HTMLOpenHandler(self.app, req, template='index.html', context=context)
        x._transforms = []
        x.get_current_user = lambda: False

        x.template = 'index.html'
        x.get()

        x = HTMLOpenHandler(self.app, req, template=None, context=context)
        x._transforms = []
        x.get_current_user = lambda: False
        x.get()

    def test_HTMLHandler(self):
        req = MagicMock()
        req.body = ''
        x = HTMLHandler(self.app, req, template='index.html', context=context)
        x._transforms = []
        x.get_current_user = lambda: False

        x.template = 'index.html'
        try:
            x.get()
            assert False
        except HTTPError:
            pass

        x = HTMLHandler(self.app, req, template=None, context=context)
        x._transforms = []
        x.get_current_user = lambda: True
        x.get()

        x = HTMLHandler(self.app, req, template='index.html', context=context)
        x._transforms = []
        x.get_current_user = lambda: b'test'
        x.get()
