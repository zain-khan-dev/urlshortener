class CommonUtils:

    @staticmethod
    def get_formatted_short_url(short_url):
        return "http://localhost:9000/v1/urls?short_url={short_url}"  # build short url