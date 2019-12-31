import os
import os.path
import logging
import tornado.ioloop
import tornado.web
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from ..utils import parse_body


class BaseHandler(tornado.web.RequestHandler):
    '''Just a default handler'''
    executor = ThreadPoolExecutor(16)

    def initialize(self, **kwargs):
        self.template_dirs = kwargs.pop("template_dirs", [os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "templates"))])
        self.template = kwargs.pop("template", "index.html")
        self.basepath = kwargs.pop("basepath", self.application.settings.get("login_manager")._options.basepath)
        self.wspath = kwargs.pop("wspath", self.application.settings.get("login_manager")._options.wspath)
        super(BaseHandler, self).initialize()

    def _set_and_raise(self, code, log_message, *args):
        logging.info(log_message, *args)
        self.set_status(code)
        raise tornado.web.HTTPError(code)

    def _set_400(self, log_message, *args):
        self._set_and_raise(400, log_message, *args)

    def _set_401(self, log_message, *args):
        self._set_and_raise(401, log_message, *args)

    def _set_403(self, log_message, *args):
        self._set_and_raise(403, log_message, *args)

    def _writeout(self, message, log_message, *args):
        logging.info(log_message, *args)
        self.set_header("Content-Type", "text/plain")
        self.write(message)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")  # FIXME
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def redirect(self, path):
        basepath = self.application.settings.get("login_manager")._options.basepath
        if path[:len(basepath)] == basepath:
            return super(BaseHandler, self).redirect(path)
        return super(BaseHandler, self).redirect(basepath + path)

    def render_template(self, template, **kwargs):
        template_dirs = self.template_dirs
        if self.settings.get('template_path', ''):
            # insert at beginnging
            template_dirs.insert(0, self.settings["template_path"])
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


class AuthenticatedHandler(BaseHandler):
    def get_current_user(self):
        cu = self.get_secure_cookie('user')
        if cu:
            return int(cu.decode("utf8"))
        return None

    def is_admin(self):
        return self.application.settings.get("login_manager").is_admin(self)

    def apikeys(self):
        return self.application.settings.get("login_manager").apikeys(self)

    def login(self, user):
        return self.application.settings.get("login_manager").login(user, self)

    def logout(self):
        return self.application.settings.get("login_manager").logout(self)

    def get_user(self):
        if self.current_user:
            return self.application.settings.get("login_manager").get_user(self.current_user)
        return None

    def get_user_from_username_password(self):
        body = parse_body(self.request)
        username_field = self.application.settings.get("login_manager")._options.user_username_field
        password_field = self.application.settings.get("login_manager")._options.user_password_field
        username = self.get_argument(username_field, body.get(username_field, ''))
        password = self.get_argument(password_field, body.get(password_field, ''))
        return self.application.settings.get("login_manager").get_user_from_username_password(username, password)

    def get_user_from_key(self):
        body = parse_body(self.request)
        key = self.get_argument('key', body.get('key', ''))
        secret = self.get_argument('secret', body.get('secret', ''))
        return self.application.settings.get("login_manager").get_user_from_key(key, secret)

    def new_apikey(self):
        return self.application.settings.get("login_manager").new_apikey(self)

    def delete_apikey(self, key_id):
        return self.application.settings.get("login_manager").delete_apikey(self, key_id)

    def redirect_home(self):
        return self.redirect(self.application.settings.get("login_manager")._options.basepath)

    def redirect_login(self):
        return self.redirect(self.application.settings.get("login_manager")._options.login_path)

    def redirect_logout(self):
        return self.redirect(self.application.settings.get("login_manager")._options.logout_path)

    def redirect_register(self):
        return self.redirect(self.application.settings.get("login_manager")._options.register_path)

    def redirect_login_html(self):
        return self.redirect(self.application.settings.get("login_manager")._options.login_html_path)

    def redirect_logout_html(self):
        return self.redirect(self.application.settings.get("login_manager")._options.logout_html_path)

    def redirect_register_html(self):
        return self.redirect(self.application.settings.get("login_manager")._options.register_html_path)

    @contextmanager
    def session(self):
        """Provide a transactional scope around a series of operations."""
        for session in self.application.settings.get("login_manager").session():
            yield session
