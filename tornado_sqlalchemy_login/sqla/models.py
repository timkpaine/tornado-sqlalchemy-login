import secrets
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

TOKEN_WIDTH = 64
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    _email = Column("email", String, nullable=False, unique=True)

    apikeys = relationship("APIKey", back_populates="user")
    admin = Column(Boolean, default=False)

    @hybrid_property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        # TODO validate
        self._email = email

    def __repr__(self):
        return "<User(id='{}', username='{}')>".format(self.id, self.username)

    def to_dict(self):
        ret = {}
        for item in ("id", "username", "email"):
            ret[item] = getattr(self, item)
        return ret

    def from_dict(self, d):
        raise NotImplementedError()


class APIKey(Base):
    __tablename__ = "apikeys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="cascade"))
    user = relationship("User", back_populates="apikeys")
    key = Column(
        String(100), nullable=False, default=lambda: secrets.token_urlsafe(TOKEN_WIDTH)
    )
    secret = Column(
        String(100), nullable=False, default=lambda: secrets.token_urlsafe(TOKEN_WIDTH)
    )

    @staticmethod
    def generateKey():
        return {
            "key": secrets.token_urlsafe(TOKEN_WIDTH),
            "secret": secrets.token_urlsafe(TOKEN_WIDTH),
        }

    def __repr__(self):
        return "<Key(id='{}', key='{}', secret='***')>".format(self.id, self.key)

    def to_dict(self):
        ret = {}
        for item in ("id", "user_id", "key", "secret"):
            ret[item] = getattr(self, item)
        return ret

    def from_dict(self, d):
        raise NotImplementedError()
