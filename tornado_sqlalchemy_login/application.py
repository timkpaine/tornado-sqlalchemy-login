from .sqla.models import User, APIKey
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class SQLAlchemyLoginManagerOptions:
    basepath: str = "/"
    apipath: str = "/api/v1/"
    wspath: str = "ws:0.0.0.0:8080/api/v1/ws/"
    login_path: str = "/api/v1/login"
    logout_path: str = "/api/v1/logout"
    register_path: str = "/api/v1/register"
    login_html_path: str = "/login"
    logout_html_path: str = "/logout"
    register_html_path: str = "/register"
    port: str = "8080"

    UserClass: object = User
    APIKeyClass: object = APIKey
    user_cookie_name: str = "user"
    user_id_field: str = "id"
    user_username_field: str = "username"
    user_password_field: str = "password"
    apikey_id_field: str = "id"
    user_apikeys_field: str = "apikeys"
    apikey_user_field: str = "user"
    user_admin_field: str = "admin"
    user_admin_value: bool = True


class _MockSession(object):
    def commit(self, *args, **kwargs): pass
    def add(self, *args, **kwargs): pass
    def refresh(self, *args, **kwargs): pass
    def rollback(self, *args, **kwargs): pass


class LoginManager(object):
    def __init__(self, options): pass
    def login(self, handler): pass
    def logout(self, handler): pass
    def register(self, handler): pass

    @contextmanager
    def session(self): yield

    def get_user(self, id): return None
    def get_user_from_username_password(self, username, password): return None
    def get_user_from_key(self, key, secret): return None


class SQLAlchemyLoginManager(LoginManager):
    def __init__(self, sessionmaker, options):
        if not isinstance(options, SQLAlchemyLoginManagerOptions):
            raise Exception("options argument must be an instance of SQLAlchemyLoginManagerOptions. Got: {}".format(type(options)))
        self._sessionmaker = sessionmaker
        self._options = options

    @contextmanager
    def session(self):
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except:  # noqa: E722
            session.rollback()
            raise
        finally:
            session.close()

    def is_admin(self, handler):
        with self.session() as session:
            user = session.query(self._options.UserClass).filter_by(**{self._options.user_id_field: handler.current_user}).first()
            if user and getattr(user, self._options.user_admin_field) == self._options.user_admin_value:
                return True
        return False

    def get_user(self, id):
        with self.session() as session:
            return session.query(self._options.UserClass).filter_by(**{self._options.user_id_field: id}).first()

    def get_user_from_username_password(self, username, password):
        if not username or not password:
            return None
        with self.session() as session:
            user = session.query(self._options.UserClass).filter_by(**{self._options.user_username_field: username}).first()
            if user and (user or not password) and (getattr(user, self._options.user_password_field) == password):
                return user
            return None

    def get_user_from_key(self, key, secret):
        if not key or not secret:
            return None
        with self.session() as session:
            apikey = session.query(self._options.APIKeyClass).filter_by(key=key).first()
            if apikey.secret != secret:
                return None
            user = getattr(apikey, self._options.apikey_user_field)
            return user

    def login(self, user, handler):
        if user and getattr(user, self._options.user_id_field):
            handler.set_secure_cookie(self._options.user_cookie_name, str(getattr(user, self._options.user_id_field)))
            return {self._options.user_id_field: str(getattr(user, self._options.user_id_field)), self._options.user_username_field: getattr(user, self._options.user_username_field)}
        return {}

    def logout(self, handler):
        handler.clear_cookie(self._options.user_cookie_name)
        return {}

    def apikeys(self, handler):
        with self.session() as session:
            user = session.query(self._options.UserClass).filter_by(**{self._options.user_id_field: int(handler.current_user)}).first()
            if not user:
                return {}
            return {str(getattr(a, self._options.apikey_id_field)): a.to_dict() for a in getattr(user, self._options.user_apikeys_field)}

    def new_apikey(self, handler):
        with self.session() as session:
            user = session.query(self._options.UserClass).filter_by(**{self._options.user_id_field: handler.current_user}).first()
            # new key
            apikey = self._options.APIKeyClass(**{self._options.apikey_user_field: user})
            session.add(apikey)
            return apikey.to_dict()

    def delete_apikey(self, handler, key_id):
        with self.session() as session:
            # delete key
            user = session.query(self._options.UserClass).filter_by(**{self._options.user_id_field: handler.current_user}).first()
            key = session.query(self._options.APIKeyClass).filter_by(**{self._options.apikey_id_field: int(handler.get_argument("id"))}).first()
            if getattr(key, self._options.apikey_user_field) == user:
                session.delete(key)
                return key.to_dict()
            return {}


def login_required():
    def _wrapper(meth):
        def _wrapper2(self):
            pass
        return _wrapper2
    return _wrapper
