from logging import getLogger
from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from datetime import datetime
import redis.asyncio as redis

from services.url_service import URLService
from utils.constants import Constants, HeaderConstants, RedisConstants
from utils.exception import RedisKeyExistsException
from utils.redis_utils import RedisUtils


router = APIRouter()

redis_client = redis.Redis()


logger = getLogger(__name__)


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


class CustomException(Exception):

    def __init__(self, *args):
        super().__init__(*args)



async def generate_short_url() -> str:
    url_counter = await redis_client.incr("url_counter")
    return encode(url_counter)



async def add_url_with_alias(long_url, short_url, expiry_in_seconds):
        if not await redis_client.setnx(RedisUtils.generate_active_url_redis_key(short_url), long_url):
            raise HTTPException(status_code=409, message="URL with the alias doesn't exists")  
        await redis_client.expire(RedisUtils.generate_active_url_redis_key(short_url), time=expiry_in_seconds)
        URLService().add_url(short_url, long_url, expiry_in_seconds)
        return short_url        


async def add_url_with_retry(long_url, expiry_in_seconds, tries=3):
    tries = Constants.DEFAULT_MAX_TRIES
    while tries > 0:
        try:
            short_url = await generate_short_url()
            if not await redis_client.setnx(RedisUtils.generate_active_url_redis_key(short_url), long_url):
                raise RedisKeyExistsException("Short URL is not unique enough")
            await redis_client.expire(RedisUtils.generate_active_url_redis_key(short_url), time=expiry_in_seconds)
            URLService().add_url(short_url, long_url, expiry_in_seconds)
            return short_url
        except RedisKeyExistsException as ex:
            logger.error("Integriy error exception - %s", repr(ex))
            # continue if tries left
        except Exception as ex:
            logger.error("Unexpected error occured, long_url - %s short_url %s exception %s", long_url, short_url, repr(ex))
            raise HTTPException(status_code=500, message="Unexpected error occured, Please try again after some time" )
        finally:
            tries -= 1
    raise HTTPException(status_code=409, message="Max retry exceeded, please try after some time")



class AddUrlRequest(BaseModel):
    alias: Optional[str] = None
    long_url: Annotated[str, Field(max_length=1000)]
    expiry_time: Optional[datetime] = None

import time

@router.post("/v1/urls")
async def add_short_url(request_body: AddUrlRequest, response: Response):
    print(request_body)
    print("here")
    alias: str|None = request_body.alias
    long_url: str = request_body.long_url
    expiry: datetime.datetime|None = request_body.expiry_time
    expiry_epoch:int = int(expiry.timestamp()) if expiry else int(datetime.now().timestamp()) + Constants.DEFAULT_EXPIRY # 10 minutes default expiry
    expiry_in_seconds = expiry_epoch - int(datetime.now().timestamp())
    if expiry_in_seconds < 0:
        return JSONResponse(content={"message": "Expiry time is before the current time"}, status_code=status.HTTP_400_BAD_REQUEST)
    if alias:
        short_url = await add_url_with_alias(long_url, expiry_in_seconds, alias)
    else:
        short_url = await add_url_with_retry(long_url, expiry_in_seconds)
    response.status_code = status.HTTP_201_CREATED
    short_url = "http://localhost:9000/v1/urls?short_url=" + short_url # build short url
    return JSONResponse(content={"message": "Generated Succesfully", "short_url": short_url}, status_code=status.HTTP_201_CREATED)
