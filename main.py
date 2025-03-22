import uvicorn
from fastapi import FastAPI

from routers.urls_router import router as url_router

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(url_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/url")
def add_url():
    return {"new_url": "this is new url created"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9102)