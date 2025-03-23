from sqlalchemy import Table, MetaData, Column, Integer, String, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class URLTable(Base):
    __tablename__ = "URLS"

    short_url = Column(String, primary_key=True,)
    long_url = Column(String)
    expiry = Column(Integer)