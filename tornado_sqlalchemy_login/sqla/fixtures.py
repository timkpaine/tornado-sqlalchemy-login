import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, User, APIKey


def main(sql_url, application_name="tornado_sqlalchemy_login", user_class=User, apikey_class=APIKey):
    '''Create dummy notebook data for sqlalchemy'''
    engine = create_engine(sql_url, echo=False)
    Base.metadata.create_all(engine)
    sm = sessionmaker(bind=engine)

    session = sm()
    admin = User(username='admin',
                 password='admin',
                 email='test@test.com',
                 admin=True)
    try:
        session.add(admin)
        session.commit()
        session.refresh(admin)
        print('added admin: {}'.format(admin))
        key = APIKey(user=admin)
        session.add(key)
        session.commit()
        session.refresh(key)
        print('added apikey: {}'.format(key))
        with open("keys.sh", "w") as fp:
            fp.write("#!/bin/bash\n")
            fp.write("export TORNADO_SQLALCHEMY_LOGIN_KEY={}\n".format(key.key))
            fp.write("export TORNADO_SQLALCHEMY_LOGIN_SECRET={}\n".format(key.secret))
    except BaseException:
        session.rollback()
        admin = session.query(User).filter_by(username='test').first()
        print('admin exists: {}'.format(admin))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("args: <sql_url>")
    else:
        main(sys.argv[1])
