from datetime import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field


class AddUrlRequest(BaseModel):
    alias: Optional[str] = None
    long_url: Annotated[str, Field(max_length=1000)]
    expiry_time: Optional[datetime] = None