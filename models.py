from sqlalchemy import Column, Integer,String, JSON, ForeignKey
from databes import Base

class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)
    description = Column(String)
    photo_link = Column(String)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key = True, index=True)
    name = Column(String, index = True)
    email = Column(String, unique = True, index = True)
    password = Column(String, index=True)

class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key = True, index = True)
    content = Column(JSON, index = True)
    price = Column(Integer, index = True)
    user_id = Column(Integer, ForeignKey(User.id))
    status = Column(String)