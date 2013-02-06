from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import app
import uuid
import author

engine = create_engine(app.config['DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    engine = create_engine(app.config['DATABASE_URI'])
    Base.metadata.create_all(bind=engine)


def import_posts():
    pass


def session_create(user):
    session = Session()
    session.session_id = str(uuid.uuid1())
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
    provider = Column(String(200))
    identity = Column(String(200))


class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    slug = Column(String(200))
    html = Column(Text())
    text = Column(Text())
    head = Column(Text())
    footer = Column(Text())
    date = Column(DateTime())


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    html = Column(Text())
    text = Column(Text())
