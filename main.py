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


# Include router
app.include_router(create_url_router)
app.include_router(get_url_router)

# Run server with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
