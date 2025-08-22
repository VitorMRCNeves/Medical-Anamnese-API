from fastapi import FastAPI
from app.routers import audio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()


app.include_router(audio.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://oniva.up.railway.app",
        "http://localhost:8045",
        "http://localhost:8005",
        "http://127.0.0.1:8005",
    ],  # Apenas seus domínios
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Trusted hosts - CONFIGURAÇÃO CORRIGIDA
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "oniva.up.railway.app",
        "localhost",
        "127.0.0.1",
    ],
)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
