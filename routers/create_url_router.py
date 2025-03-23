from typing import Annotated, Optional
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from datetime import datetime
import redis.asyncio as redis

from services.url_service import URLService
from utils.constants import Constants, HeaderConstants, RedisConstants


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


class CustomException(Exception):

    def __init__(self, *args):
        super().__init__(*args)



async def create_short_url() -> str:
    url_counter = await redis_client.incr("url_counter")
    return encode(url_counter)

async def  add_url_with_retry(long_url, expiry_in_seconds, tries=1, short_url=None):
    while tries > 0:
        try:
            short_url = short_url or await create_short_url()
            if not await redis_client.setnx(f"urls:{short_url}", long_url):
                raise CustomException("Short URL is not unique enough")
            await redis_client.expire(f"urls:{short_url}", time=expiry_in_seconds)
            URLService().add_url(short_url, long_url, expiry_in_seconds)
            return status.HTTP_201_CREATED, short_url
        except CustomException as ex:
            print("Integrity error", repr(ex))
            return status.HTTP_409_CONFLICT, None
        except Exception as ex:
            print(repr(ex))
            return status.HTTP_500_INTERNAL_SERVER_ERROR, None
        finally:
            tries -= 1
    return status.HTTP_409_CONFLICT, None


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
    status_code, short_url = await add_url_with_retry(long_url, expiry_in_seconds, short_url=alias)
    print(status_code, short_url)
    response.status_code = status_code
    if status_code == status.HTTP_201_CREATED:
        return JSONResponse(content={"message": "Generated Succesfully", "short_url": short_url}, status_code=status.HTTP_201_CREATED)
