import os
import os.path
import logging
import tornado.ioloop
import tornado.web
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from ..web import parse_body


class BaseHandler(tornado.web.RequestHandler):
    '''Just a default handler'''
    executor = ThreadPoolExecutor(16)

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
        if path[:len(self.basepath)] == self.basepath:
            return super(BaseHandler, self).redirect(path)
        return super(BaseHandler, self).redirect(self.basepath + path)

    def render_template(self, template, **kwargs):
        if hasattr(self, 'template_dirs'):
            template_dirs = self.template_dirs
        else:
            template_dirs = [os.path.join(os.path.dirname(__file__), "..", "assets", "templates")]

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


class AuthenticatedHandler(BaseHandler):
    def get_current_user(self):
        cu = self.get_secure_cookie('user')
        if cu:
            return self.application.settings.get("login_manager").get_user(cu.decode("utf8"))
        return None

    def is_admin(self):
        return self.application.settings.get("login_manager").is_admin(self)

    def login(self, user):
        return self.application.settings.get("login_manager").login(user, self)

    def logout(self):
        return self.application.settings.get("login_manager").logout(self)

    def get_user_from_username_password(self):
        body = parse_body(self.request)
        username = self.get_argument('username', body.get('username', ''))
        password = self.get_argument('password', body.get('password', ''))
        return self.application.settings.get("login_manager").get_user_from_username_password(username, password)

    def get_user_from_key(self):
        body = parse_body(self.request)
        key = self.get_argument('key', body.get('key', ''))
        secret = self.get_argument('secret', body.get('secret', ''))
        return self.application.settings.get("login_manager").get_user_from_key(key, secret)

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
