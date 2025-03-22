from db.engine import engine, Session
from db.url_table import URLTable
from sqlalchemy.exc import SQLAlchemyError

class URLService:


    def add_url(self, short_url, long_url, expiry):
        try:
            session = Session()
            new_url = URLTable(short_url=short_url, long_url=long_url, expiry=expiry)
            session.add(new_url)
            session.commit()
            return True
        except SQLAlchemyError as ex:
            session.rollback()  
            print(f"Database error: {ex}")
            return False
        except Exception as ex:
            if session:
                session.rollback()
            print(f"Unexpected error: {repr(ex)}")
            return False
        finally:
            session.close()

    def get_url(self, short_url):
        with Session() as session:
            url_mapping = session.query(URLTable).filter(URLTable.short_url == short_url).first()
            return url_mapping
