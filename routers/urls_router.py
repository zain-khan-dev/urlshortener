from fastapi import APIRouter, Response, status
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from models.AddURLRequest import AddUrlRequest
import datetime
import redis.asyncio as redis

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


def create_short_url() -> str:
    url_counter = redis_client.incr("url_counter")
    return encode(url_counter)

def add_url_with_retry(long_url, expiry_in_seconds, tries=1, short_url=None):
    while tries > 0:
        try:
            short_url = short_url or create_short_url()
            if not redis_client.setnx(f"urls:{short_url}", long_url):
                raise IntegrityError
            redis_client.expire(f"urls:{short_url}", time=expiry_in_seconds)
            URLService().add_url(short_url, long_url, expiry_in_seconds)
            return status.HTTP_201_CREATED, short_url
        except IntegrityError:
            pass
        except Exception as ex:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, None
        finally:
            tries -= 1
    return status.HTTP_409_CONFLICT, None


@router.post("/v1/urls")
def add_short_url(request_body: AddUrlRequest, response: Response):
    short_url: str|None = request_body.short_url
    long_url: str = request_body.long_url
    expiry: datetime.datetime = request_body.expiry_time
    expiry_epoch:int = int(expiry.timestamp())
    expiry_in_seconds = expiry_epoch - int(datetime.datetime.now().timestamp())
    if expiry_in_seconds < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    status_code, short_url = add_url_with_retry(long_url, expiry_in_seconds, short_url=short_url)
    response.status_code = status_code
    if status_code == status.HTTP_201_CREATED:
        return {"short_url": short_url}


class RedisKeyNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def is_url_expired(url_mapping):
    if url_mapping.expiry_time - int(datetime.datetime.now().timestamp()) < 0:
        return True
    return False


def get_url_expiry_ttl(expiry_time):
    return expiry_time - int(datetime.datetime.now().timestamp())


@router.get("/v1/urls")
async def get_url(short_url: str, response:Response):
    try:
        long_url:bytes = await redis_client.get(f"urls:{short_url}")
        if not long_url:
            if await redis_client.exists(f"expired_urls:{short_url}"):
                response.status_code = status.HTTP_404_NOT_FOUND
                return
            else:
                raise RedisKeyNotFoundException
        else:
            response.status_code = status.HTTP_302_FOUND
            response.headers["Location"] = long_url.decode("utf-8")
    except RedisKeyNotFoundException:
        url_mapping = URLService().get_url(short_url)
        if not url_mapping or is_url_expired(url_mapping):
            # to handle expired or url not existing, next time will be present in redis
            await redis_client.set(f"expired_urls:{short_url}", "1", ex=60*60) # set expiry 1 hour
        else:
            await redis_client.set(f"urls:{short_url}", url_mapping.long_url, ex=get_url_expiry_ttl(
                url_mapping.expiry_time))
            response.status_code = status.HTTP_302_FOUND
            response.headers["Location"] = url_mapping.long_url

