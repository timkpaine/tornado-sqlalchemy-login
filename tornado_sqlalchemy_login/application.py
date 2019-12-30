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
