from fastapi import FastAPI
from app.routers import audio

app = FastAPI()


app.include_router(audio.router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

