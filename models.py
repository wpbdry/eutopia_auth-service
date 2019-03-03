from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://localhost/eut-auth', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
# necessary for querying
Base.query = db_session.query_property()

class User(Base):
    __table_args__ = {'schema' : 'auth'}
    __tablename__ = 'user'

    uid = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
