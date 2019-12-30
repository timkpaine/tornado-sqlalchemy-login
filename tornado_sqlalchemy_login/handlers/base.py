import logging
import tornado.ioloop
import tornado.web
import ujson
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from ..sqla.models import User, APIKey
from ..utils import parse_body


class ServerHandler(tornado.web.RequestHandler):
    '''Just a default handler'''
    executor = ThreadPoolExecutor(16)

    def get_current_user(self):
        cu = self.get_secure_cookie('user')
        if cu:
            return cu.decode("utf8")
        return None

    def is_admin(self):
        with self.session() as session:
            user = session.query(self.user_sql_class).filter_by(**{self.user_id_field: self.current_user}).first()
            if user and getattr(user, self.user_admin_field) == self.user_admin_value:
                return True
        return False

    def get_user_from_username_password(self):
        body = parse_body(self.request)
        username = self.get_argument('username', body.get('username', ''))
        password = self.get_argument('password', body.get('password', ''))
        if not username or not password:
            return 0
        with self.session() as session:
            user = session.query(self.user_sql_class).filter_by(username=username).first()
            if user and (user or not password) and (user.password == password):
                self.login(user)
                return getattr(user, self.user_id_field)
            else:
                return 0

    def get_user_from_key(self):
        body = parse_body(self.request)
        key = self.get_argument('key', body.get('key', ''))
        secret = self.get_argument('secret', body.get('secret', ''))
        if not key or not secret:
            return 0
        with self.session() as session:
            apikey = session.query(self.apikey_sql_class).filter_by(key=key).first()
            if apikey.secret != secret:
                return 0
            self.login(getattr(apikey, self.apikey_user_field))
            return getattr(getattr(apikey, self.apikey_user_field), self.user_id_field)

    def _set_400(self, log_message, *args):
        logging.info(log_message, *args)
        self.set_status(400)
        self.finish('{"error":"400"}')
        raise tornado.web.HTTPError(400)

    def _set_401(self, log_message, *args):
        logging.info(log_message, *args)
        self.set_status(401)
        self.finish('{"error":"401"}')
        raise tornado.web.HTTPError(401)

    def _set_403(self, log_message, *args):
        logging.info(log_message, *args)
        self.set_status(403)
        self.finish('{"error":"403"}')
        raise tornado.web.HTTPError(403)

    def _writeout(self, message, log_message, *args):
        logging.info(log_message, *args)
        self.set_header("Content-Type", "text/plain")
        self.write(message)

    def _validate(self, validation_method=None):
        return validation_method(self) if validation_method else {}

    def login(self, user):
        ret = self._login_post(user)
        self._writeout(ujson.dumps(ret), "Registering user %s", ret[self.user_id_field])

    def _login_post(self, user):
        if user and getattr(user, self.user_id_field) and getattr(user, self.user_id_field) in self._users:
            self._set_login_cookie(user)
            return {self.user_id_field: str(getattr(user, self.user_id_field)), 'username': user.username}

        elif user and getattr(user, self.user_id_field):
            self._users[getattr(user, self.user_id_field)] = user
            self._set_login_cookie(user)
            return {self.user_id_field: str(getattr(user, self.user_id_field)), 'username': user.username}
        else:
            return False

    def _set_login_cookie(self, user):
        self.set_secure_cookie('user', str(getattr(user, self.user_id_field)))

    @contextmanager
    def session(self):
        """Provide a transactional scope around a series of operations."""
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except:  # noqa: E722
            session.rollback()
            raise
        finally:
            session.close()

    def redirect(self, path):
        if path[:len(self.basepath)] == self.basepath:
            return super(ServerHandler, self).redirect(path)
        return super(ServerHandler, self).redirect(self.basepath + path)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")  # FIXME
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def render_template(self, template, **kwargs):
        if hasattr(self, 'template_dirs'):
            template_dirs = self.template_dirs
        else:
            template_dirs = []

        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )
        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(self.template)
        except TemplateNotFound:
            raise TemplateNotFound(self.template)

        kwargs['current_user'] = self.current_user if self.current_user else ''
        kwargs['basepath'] = self.basepath
        kwargs['wspath'] = self.wspath
        content = template.render(**kwargs)
        return content

    def initialize(self,
                   sessionmaker=None,
                   UserSQLClass=User,
                   APIKeySQLClass=APIKey,
                   user_id_field='id',
                   apikey_id_field='id',
                   user_apikeys_field='apikeys',
                   apikey_user_field='user',
                   user_admin_field='admin',
                   user_admin_value=True,
                   basepath='/',
                   wspath='ws:localhost:8080/',
                   template='404.html',
                   template_dirs=None,
                   *args,
                   **kwargs):
        '''Initialize the base handler

        Args:
            sessionmaker: A SQLAlchemy sessionmaker object
            UserSQLClass: the SQLAlchemy class representing a user
            APIKeySQLClass: the SQLALchemy class representing an API Key. Expected fields are "key" and "secret"

            user_id_field (str): The field in an instance of UserSQLClass to look for the user's unique id
            apikey_id_field (str): The field in an instance of APIKeySQLClass to look for the apikey's unique id
            user_apikeys_field (str): The field in an instance of UserSQLClass to look for the apikeys (expected relationship)
            apikey_user_field (str): The field in an instance of APIKeySQLClass to look for the user (expected relationship)
            user_admin_field (str): The field in an instance of UserSQLClass that specifies a user's admin status
            user_admin_value (str): The value that will be set in the above field if the user is an admin

            basepath (str): the base path for the webserver
            wspath (str): the base path for the webserver's websocket (specify ws or wss as well, port will be autofilled)

            template(str): jinja2 template to user for the html serving handler
            template_dirs (list): folders to look for the above template
        '''
        super(ServerHandler, self).initialize()
        self._sessionmaker = sessionmaker

        # query fields
        self.user_sql_class = UserSQLClass
        self.user_id_field = user_id_field
        self.apikey_id_field = apikey_id_field
        self.user_apikeys_field = user_apikeys_field
        self.apikey_user_field = apikey_user_field
        self.user_admin_field = user_admin_field
        self.user_admin_value = user_admin_value
        self.apikey_sql_class = APIKeySQLClass

        # Fetch users
        self._users = {getattr(u, self.user_id_field): u for u in self._sessionmaker().query(self.user_sql_class).all()}

        # template globals
        self.basepath = basepath
        self.wspath = wspath

        # jinja2 templates
        self.template = template
        self.template_dirs = template_dirs or []

        # pass through the rest
        for k, v in kwargs.items():
            setattr(self, k, v)
