from .base import AuthenticatedHandler


class LoginHandler(AuthenticatedHandler):
    def get(self):
        if self.current_user:
            self.redirect("api/v1/register")
        else:
            self.redirect_home()

    def post(self):
        # Get from current user
        user = self.get_user()
        # Get from username/password
        if not user:
            user = self.get_user_from_username_password()
        # get from apikey/secret
        if not user:
            user = self.get_user_from_key()
        if user:
            # return data in json
            self.finish(self.login(user))
            return
        # set 401
        self._set_401("User not recognized")


class LogoutHandler(AuthenticatedHandler):
    def get(self):
        self.logout()
        self.redirect_home()

    def post(self):
        self.logout()
