from .base import BaseHandler


class HTMLHandler(BaseHandler):
    def initialize(self, template=None, basepath="/", wspath="/", **kwargs):
        super(HTMLHandler, self).initialize(template=template, basepath=basepath, wspath=wspath, **kwargs)

    def get(self):
        '''Get the login page'''
        template = self.render_template(self.template)
        self.write(template)
