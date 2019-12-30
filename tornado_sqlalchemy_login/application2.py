from dataclasses import dataclass
from .sqla import User, APIKey

# from tornado.web import Application
# self.application.settings.get('blarg')


@dataclass
class SQLAlchemyLoginConfiguration:
    basepath: str = "/"
    apipath: str = "/api/{api_revision}/"
    wspath: str = "ws:{hostname}:{port}/{apipath}/ws/"
    login_path: str = "/login"
    logout_path: str = "/logout"
    register_path: str = "/register"
    hostname: str = "localhost"
    port: str = "8080"
    api_revision: str = "v1"


@dataclass
class SQLAlchemyLoginManagerOptions:
    UserSQLClass: object = User
    APIKeySQLClass: object = APIkey
    user_id_field: str = "id"
    apikey_id_field: str = "id"
    user_apikeys_field: str = "apikeys"
    apikey_user_field: str = "user"
    user_admin_field: str = "admin"
    user_admin_value: bool = True


class SQLAlchemyLoginManager(object):
    def __init__(self, sqlalchemy_sessionmaker, options):
        if not isinstance(options, SQLAlchemyLoginManagerOptions):
            raise Exception("options argument must be an instance of SQLAlchemyLoginManagerOptions. Got: {}".format(type(options))
        pass


def login():
    def _wrapper(meth):
        def _wrapper2(self):
            pass
        return _wrapper2
    return _wrapper
