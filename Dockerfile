# ============================================================
#  Dockerfile — Datathon Passos Mágicos
#  Imagem otimizada para servir a API FastAPI com Uvicorn
# ============================================================

FROM python:3.10-slim

# Evitar prompts interativos e buffering de logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Diretório de trabalho dentro do container
WORKDIR /app

# Copiar e instalar dependências primeiro (cache de camada Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte, modelo, testes e frontend
COPY app/ ./app/
COPY src/ ./src/
COPY modelos/ ./modelos/
COPY tests/ ./tests/
COPY frontend/ ./frontend/

# Expor a porta da API
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
