from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from author import app
import uuid

engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    engine = create_engine(app.config['DATABASE_URI'])
    Base.metadata.create_all(bind=engine)

def session_create(user):
    import uuid
    session = Session()
    session.session_id =  str(uuid.uuid1())
    session.user_id = user.id
    db_session.add(session)
    db_session.commit()
    return session.session_id

def session_get(session_id):
    session = Session.query.filter_by(session_id=session_id).first()
    return session

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    email = Column(String(200))
    website = Column(String(200))
    openid = Column(String(200))
    oauth_token = Column(String(200))
    oauth_secret = Column(String(200))
    google_id = Column(String(200))

    def __init__(self, name):
        self.name = name


class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(20))
    user_id = Column(Integer, ForeignKey('users.id'))
