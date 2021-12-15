from sqlalchemy import create_engine, MetaData, Table, Integer, String, Column, Text
from sqlalchemy.ext.declarative import declarative_base
import pathlib

BASE_DIR = pathlib.Path(__file__).parent
Base = declarative_base()
engine = create_engine('sqlite:///' + str(BASE_DIR /"dogs.sqlite3"))


class dogs(Base):
    __tablename__ = 'dogs'

    item_id = Column(String(36), primary_key=True, unique=True)
    item_url = Column(String, unique=True)
    name = Column(String)
    description = Column(Text)
    price = Column(String)
    photo_url = Column(String, unique=True)

    def __init__(self, item_id, name, description, price, photo_url, item_url):
        self.item_id = item_id
        self.name = name
        self.description = description
        self.price = price
        self.photo_url = photo_url
        self.item_url = item_url


Base.metadata.create_all(engine)
