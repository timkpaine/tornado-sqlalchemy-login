import tornado.web
import copy
from .base import ServerHandler


def get_kwargs(handler, template_kwargs):
    kwargs = copy.deepcopy(template_kwargs)
    for k in kwargs:
        if callable(kwargs[k]):
            kwargs[k] = kwargs[k](handler)
    return kwargs


class HTMLOpenHandler(ServerHandler):
    def initialize(self, context=None, template=None, template_kwargs=None, **kwargs):
        super(HTMLOpenHandler, self).initialize(template=template, **(context or {}))
        self.template_kwargs = template_kwargs or {}

    def get(self, *args):
        '''Get the login page'''
        if not self.template:
            self.redirect(self.basepath)
        else:
            if 'logout' in self.request.path:
                self.clear_cookie("user")

            # TODO hack
            kwargs = get_kwargs(self, self.template_kwargs)
            # endhack

            template = self.render_template(self.template, **kwargs)
            self.write(template)

    def post(self, *args):
        with self.session() as session:
            if 'login' in self.request.path:
                user = self.get_argument('id', '') or self.current_user.decode('utf-8') or -1
                ret = session.query(self.user_sql_class).filter_by(**{self.user_id_field: int(user)}).first()
                if not ret.id:
                    self.redirect(self.basepath + 'login')
                    return
                self._login_post(ret)
            elif 'register' in self.request.path:
                c = self.user_sql_class()
                session.add(c)
                session.commit()
                session.refresh(c)
                if not ret:
                    self.redirect(self.basepath + 'login')
                    return
                self._login_post(c)
            self.redirect(self.get_argument('next', self.basepath))


class HTMLHandler(HTMLOpenHandler):
    @tornado.web.authenticated
    def get(self, *args):
        '''Get the login page'''
        if not self.template:
            self.redirect('')
        else:
            # TODO hack
            kwargs = get_kwargs(self, self.template_kwargs)
            # endhack

            template = self.render_template(self.template, **kwargs)
            self.write(template)
