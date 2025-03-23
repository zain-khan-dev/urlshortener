from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sql_url = "sqlite:////home/zain/tempdb/newdb.db"

engine = create_engine(sql_url)

Session = sessionmaker(engine)
print(Session())