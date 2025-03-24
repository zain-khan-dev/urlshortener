import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers.get_url_router import router as get_url_router
from routers.create_url_router import router as create_url_router
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

origins = [
    "http://localhost:3000",  # Frontend origin
    "*"  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

import traceback
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("custom_middleware")

class DebugPydanticMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request normally
            response = await call_next(request)
            return response
        except RequestValidationError as e:
            # If there's a validation error, log the details
            logger.error(f"Validation error occurred: {e}")
            
            # Log the detailed error traceback for debugging
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # You can also log the request body if necessary for debugging
            request_body = await request.json()
            logger.error(f"Request body: {request_body}")
            
            # Customize the error response
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Validation failed",
                    "details": e.errors(),
                    "request_body": request_body
                }
            )



app.add_middleware(DebugPydanticMiddleware)


# Include router
app.include_router(create_url_router)
app.include_router(get_url_router)

# Run server with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
