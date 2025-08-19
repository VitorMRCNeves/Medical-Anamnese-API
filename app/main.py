from fastapi import FastAPI
from app.routers import audio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()


app.include_router(audio.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://djagomedical-production.up.railway.app"
    ],  # Apenas seus domínios
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["djagomedical-production.up.railway.app"]
)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
