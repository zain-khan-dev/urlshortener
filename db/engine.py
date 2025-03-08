from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sql_url = "sqlite:///C:/Users/zaink/Desktop/projects/systemdesign/urlshortener/newtable.db"

engine = create_engine(sql_url)

Session = sessionmaker(engine)