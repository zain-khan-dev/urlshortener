import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers.urls_router import router as url_router
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom middleware for logging requests
class LogRequestMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # Log the incoming request
        if scope["type"] == "http":
            logger.info(f"Request: {scope['method']} {scope['path']}")
        
        # Call the next middleware or route handler
        await self.app(scope, receive, send)

app = FastAPI()

# Add the custom logging middleware before the CORS middleware
app.add_middleware(LogRequestMiddleware)

# CORS configuration
origins = [
    "http://localhost:3000",  # Frontend origin
    "*"  # Allow all origins
]

# Add CORS middleware globally
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(url_router)

# Test root route
@app.get("/")
def read_root():
    return {"Hello": "World"}

# Another test route
@app.post("/url")
def add_url():
    return {"new_url": "this is new url created"}

# Run server with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
