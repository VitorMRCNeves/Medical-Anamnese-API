from fastapi import FastAPI
from app.routers import audio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

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

# Configuração de hosts confiáveis baseada no ambiente
IS_PRODUCTION = (
    os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("PORT") is not None
)

if IS_PRODUCTION:
    # Em produção, seja mais permissivo com IPs internos
    trusted_hosts = [
        "oniva.up.railway.app",
        "*",  # Railway usa IPs dinâmicos internos
    ]
else:
    # Em desenvolvimento, seja mais restritivo
    trusted_hosts = [
        "localhost",
        "127.0.0.1",
        "localhost:8005",
        "127.0.0.1:8005",
    ]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=trusted_hosts,
)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
