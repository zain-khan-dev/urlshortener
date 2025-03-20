from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field, BeforeValidator


def parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, str):
        return datetime.fromisoformat(value)  # Handle ISO strings
    return value


class AddUrlRequest(BaseModel):
    alias: Optional[str] = None
    long_url: Annotated[str, Field(max_length=1000)]
    expiry_time: datetime