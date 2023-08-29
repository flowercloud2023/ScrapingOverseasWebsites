from sqlalchemy import *
import pymysql
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
database = 'mysql+pymysql:'

Base = declarative_base()
# 创建数据库连接对象
engine = create_engine(database)
DBSession = sessionmaker(bind=engine)
SQLsession = DBSession()

# ORM
class Infos(Base):
    __tablename__ = 'spiders_infos'
    id = Column(Integer(), primary_key=True)
    code = Column(String(255))
    name = Column(String(255))
    bio = Column(String(255))
    website = Column(String(2000))
    category = Column(String(255))
    phone = Column(String(255))
    email = Column(String(255))
    address = Column(String(255))
    groups = Column(String(255))
    source = Column(String(255))
    status = Column(Integer(), default=1)
    remark = Column(Text)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


class Comments(Base):
    __tablename__ = 'spiders_comments'
    id = Column(Integer(), primary_key=True)
    source = Column(String(255))
    content = Column(Text)
    comment_date = Column(String(255))
    score = Column(String(255))
    status = Column(Integer(), default=1)
    remark = Column(Text)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())


Base.metadata.create_all(engine)

def read_txt():
    f = open(f'{os.path.dirname(os.path.abspath(__file__))}\\locations.txt', 'r')
    text = f.read().split('\n')
    f.close()
    return text