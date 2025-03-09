from db.engine import engine, Session
from db.url_table import URLTable


class URLService:

    def add_url(self, short_url, long_url, expiry):
        with Session() as session:
            new_url = URLTable(short_url=short_url, long_url=long_url, expiry=expiry)
            session.add(new_url)
            session.commit()


    def get_url(self, short_url):
        with Session() as session:
            url_mapping = session.query(URLTable).filter(URLTable.short_url == short_url).first()
            return url_mapping
