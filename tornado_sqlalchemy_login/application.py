import os.path
import logging
import tornado.ioloop
import tornado.web
from .handlers import ServerHandler, \
    HTMLOpenHandler, \
    LoginHandler, \
    LogoutHandler, \
    RegisterHandler, \
    APIKeyHandler

DEFAULT_API_REVISION = 'v1'
DEFAULT_BASEPATH = '/'
DEFAULT_API_PATH = '/api/{}'


class TornadoApplication(object):
    def __init__(self):
        # Server settings
        self._port = '8080'
        self._debug = False
        self._assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        self._static_dir = os.path.join(os.path.dirname(__file__), 'assets', 'static')
        self._cookie_secret = ''
        # Handler settings
        self._basepath = '/'
        self._apipath = '/api/v1/'
        self._wspath = 'ws:0.0.0.0:{port}/'
        self._sqlalchemy_sessionmaker = None
        self._UserSQLClass = None
        self._APIKeySQLClass = None
        self._user_id_field = 'id'
        self._apikey_id_field = 'id'
        self._user_apikeys_field = 'apikeys'
        self._apikey_user_field = 'user'
        self._user_admin_field = 'admin'
        self._user_admin_value = True
        # extra
        self._extra_handlers = None
        self._extra_context = None
        self._api_revision = 'v1'

    @property
    def port(self): return self._port

    @port.setter
    def port(self, value):
        # update wspath if applicable
        pass


def make_application(
        # Server settings
        port='8080',
        debug=False,
        assets_dir=os.path.join(os.path.dirname(__file__), 'assets'),
        static_dir=os.path.join(os.path.dirname(__file__), 'assets', 'static'),
        cookie_secret='',
        # Handler settings
        basepath='/',
        apipath='/api/v1/',
        wspath='ws:0.0.0.0:{port}/',
        sqlalchemy_sessionmaker=None,
        UserSQLClass=None,
        APIKeySQLClass=None,
        user_id_field='id',
        apikey_id_field='id',
        user_apikeys_field='apikeys',
        apikey_user_field='user',
        user_admin_field='admin',
        user_admin_value=True,
        # extras
        extra_handlers=None,
        extra_context=None,
        api_revision='v1'):

    extra_handlers = extra_handlers or []
    extra_context = extra_context or {}

    # Port
    port = int(os.environ.get('PORT', port))

    # Set websocket path
    wspath = wspath.format(port)
    context = {'sessionmaker': sqlalchemy_sessionmaker,
               'basepath': basepath,
               'wspath': wspath,
               'UserSQLClass': UserSQLClass,
               'APIKeySQLClass': APIKeySQLClass,
               'user_id_field': user_id_field,
               'apikey_id_field': apikey_id_field,
               'user_apikeys_field': user_apikeys_field,
               'apikey_user_field': apikey_user_field,
               'user_admin_field': user_admin_field,
               'user_admin_value': user_admin_value}

    default_handlers = extra_handlers + [
        (r"/", HTMLOpenHandler, {'template': 'index.html', 'context': context}),
        (r"/index.html", HTMLOpenHandler, {'template': 'index.html', 'context': context}),
        (r"/api/{}/login".format(api_revision), LoginHandler, context),
        (r"/api/{}/logout".format(api_revision), LogoutHandler, context),
        (r"/api/{}/register".format(api_revision), RegisterHandler, context),
        (r"/api/{}/apikeys".format(api_revision), APIKeyHandler, context),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_dir}),
        (r"/(.*)", HTMLOpenHandler, {'template': '404.html', 'context': context})
    ]

    for _, handler, handler_kwargs in extra_handlers:
        if issubclass(handler, HTMLOpenHandler):
            if 'context' in handler_kwargs:
                handler_kwargs['context'].update(context)
            else:
                handler_kwargs['context'] = context

        elif issubclass(handler, ServerHandler):
            handler_kwargs.update(context)

    settings = {
        "cookie_secret": cookie_secret,
        "login_url": basepath + "login",
        "debug": debug,
        "template_path": os.path.join(assets_dir, 'templates'),
    }

    application = tornado.web.Application(default_handlers, **settings)

    logging.critical('LISTENING: %d', port)
    application.listen(port)
    return application
