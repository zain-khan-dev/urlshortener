import uvicorn
from fastapi import FastAPI

from routers.urls_router import router as url_router

app = FastAPI()


app.include_router(url_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/url")
def add_url():
    return {"new_url": "this is new url created"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)