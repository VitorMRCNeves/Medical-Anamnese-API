from fastapi import FastAPI
from app.routers.audio import audio_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config.ConfigDependencies import AppConfigs


deps = AppConfigs.load_dependencies()
app = FastAPI()


app.include_router(audio_router(deps))

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


if deps.is_production:

    trusted_hosts = [
        "oniva.up.railway.app",
        "*",
    ]
else:
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
    return {"status": "ok"}
