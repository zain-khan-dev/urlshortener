from fastapi import APIRouter

from models.AddURLRequest import AddUrlRequest
import datetime
import redis

from services.url_service import URLService

router = APIRouter()

redis_client = redis.Redis()

def convert_to_digit(val: int) -> chr:
    if 0 <= val < 26:
        # Small letters
        return chr(ord('a') + val)
    elif 26 <= val < 52:
        return chr(ord('A') + (val - 26))
    else:
        return chr(val - 52)


def encode(counter: int):
    """
        Converts number to 62 bit encoded string
    :param counter:
    :return:
    """
    result = []
    while(counter > 0):
        mod_val = counter%62
        result.append(convert_to_digit(mod_val))
        counter //= 62
    return ''.join(reversed(result))


@router.post("/v1/urls")
def add_short_url(request_body: AddUrlRequest):
    print(request_body)
    short_url: str|None = request_body.short_url
    long_url: str = request_body.long_url
    expiry: datetime.datetime = request_body.expiry_time
    if not short_url:
        print(expiry.timestamp())
        url_counter = redis_client.incr("url_counter")
        short_url = encode(url_counter)
    try:
        URLService().add_url(short_url, long_url, expiry)
    except Exception as ex:
        print(ex)
    print(short_url)
    return {"short_url": short_url}
