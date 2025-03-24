from fastapi import APIRouter, Response, status

import datetime
import redis.asyncio as redis

from services.url_service import URLService
from utils.constants import HeaderConstants, RedisConstants
from utils.exception import RedisKeyNotFoundException

router = APIRouter()

redis_client = redis.Redis()


def is_url_expired(url_mapping):
    if url_mapping.expiry_time - int(datetime.datetime.now().timestamp()) < 0:
        return True
    return False


def get_url_expiry_ttl(expiry_time):
    return expiry_time - int(datetime.datetime.now().timestamp())



@router.get("/v1/urls")
async def get_url(short_url: str, response:Response):
    try:
        long_url:bytes = await redis_client.get(f"{RedisConstants.URL_NAMESPACE}:{short_url}")
        if not long_url:
            if await redis_client.exists(f"{RedisConstants.EXPIRED_URL_KEY_NAMESPACE}:{short_url}"):
                response.status_code = status.HTTP_404_NOT_FOUND
                return
            else:
                raise RedisKeyNotFoundException
        else:
            print(long_url.decode("utf-8"))
            response.status_code = status.HTTP_302_FOUND
            response.headers[HeaderConstants.LOCATION] = long_url.decode("utf-8")
            return response
    except RedisKeyNotFoundException:
        url_mapping = URLService().get_url(short_url)
        if not url_mapping or is_url_expired(url_mapping):
            # to handle expired or url not existing, next time will be present in redis
            await redis_client.set(f"{RedisConstants.EXPIRED_URL_KEY_NAMESPACE}:{short_url}", RedisConstants.EXPIRED_URL_EXISTS_VALUE, ex=60*60) # set expiry 1 hour
        else:
            await redis_client.set(f"{RedisConstants.URL_NAMESPACE}:{short_url}", url_mapping.long_url, ex=get_url_expiry_ttl(
                url_mapping.expiry_time))
            response.status_code = status.HTTP_302_FOUND
            response.headers[HeaderConstants.LOCATION] = url_mapping.long_url

