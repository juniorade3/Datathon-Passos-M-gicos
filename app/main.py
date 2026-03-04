"""
Módulo principal da API FastAPI.

Inicializa a aplicação FastAPI, configura logging estruturado,
instrumentação Prometheus, CORS e serve o frontend estático.
"""

import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.drift import drift_router
from app.routes import router

# =====================================================================
#  Logging estruturado (JSON)
# =====================================================================

LOG_FORMAT = (
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
    '"logger": "%(name)s", "message": "%(message)s"}'
)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("passos_magicos")


# =====================================================================
#  Inicialização da aplicação
# =====================================================================

app = FastAPI(
    title="API Passos Mágicos — Predição de Defasagem Escolar",
    description=(
        "API para prever o risco de defasagem escolar de alunos "
        "da Associação Passos Mágicos utilizando um modelo de "
        "Machine Learning (Random Forest)."
    ),
    version="1.0.0",
)

# CORS — permitir chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas da API
app.include_router(router)
app.include_router(drift_router)

# Instrumentação Prometheus — expõe /metrics automaticamente
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# =====================================================================
#  Frontend estático
# =====================================================================

FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "frontend"
)

if os.path.isdir(FRONTEND_DIR):
    @app.get("/app", tags=["Frontend"], include_in_schema=False)
    def serve_frontend():
        """Serve a página principal do frontend."""
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_DIR),
        name="frontend",
    )

    logger.info("Frontend estático montado em /app")


logger.info("API Passos Mágicos inicializada com sucesso")


@app.get("/", tags=["Health Check"])
def health_check():
    """Verifica se a API está no ar."""
    return {
        "status": "ok",
        "mensagem": "API Passos Mágicos está funcionando!",
    }
