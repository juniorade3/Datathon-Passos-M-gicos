# 🐳 Deploy e Infraestrutura

## 1. Opções de Deploy

| Método               | Complexidade | Serviços               |
|----------------------|--------------|------------------------|
| Docker Compose       | Fácil        | API + Testes + Observ. |
| Docker (só API)      | Mínima       | Apenas API             |
| Local (sem Docker)   | Manual       | Apenas API             |

## 2. Docker Compose (Recomendado)

### Pré-requisitos

- Docker 20+ e Docker Compose v2
- Portas livres: 8000, 9090, 3000, 3100

### Comandos

```bash
# Buildar e subir tudo (6 serviços)
docker compose up -d --build

# Ver logs dos testes
docker compose logs tests

# Verificar saúde da API
docker compose ps

# Parar tudo
docker compose down

# Remover volumes (limpar dados)
docker compose down -v
```

### Serviços (6 containers)

| Serviço      | Container                 | Porta  | Descrição                    |
|--------------|---------------------------|--------|------------------------------|
| `api`        | `passos-magicos-api`      | 8000   | FastAPI + Frontend + Métricas|
| `tests`      | `passos-magicos-tests`    | —      | pytest (executa uma vez)     |
| `prometheus` | `passos-magicos-prometheus`| 9090  | Coleta de métricas           |
| `grafana`    | `passos-magicos-grafana`  | 3000   | Dashboards de monitoramento  |
| `loki`       | `passos-magicos-loki`     | 3100   | Agregação de logs            |
| `promtail`   | `passos-magicos-promtail` | —      | Coletor de logs Docker       |

### Health Check

A API possui health check configurado no Docker Compose:

```yaml
healthcheck:
  test: ["CMD", "python", "-c",
         "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 15s
```

### Dependências entre Serviços

```
tests ──depends_on──▶ api (service_healthy)
prometheus ──depends_on──▶ api (service_healthy)
promtail ──depends_on──▶ loki
grafana ──depends_on──▶ prometheus, loki
```

### Rede e Volumes

- **Rede:** `observability` (bridge) — comunicação interna entre containers
- **Volumes persistentes:**
  - `prometheus_data` — dados do Prometheus (retenção: 7 dias)
  - `loki_data` — logs do Loki
  - `grafana_data` — state do Grafana

## 3. Dockerfile

```dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Cache de camada: dependências primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Código, modelo, testes e frontend
COPY app/ ./app/
COPY src/ ./src/
COPY modelos/ ./modelos/
COPY tests/ ./tests/
COPY frontend/ ./frontend/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Otimizações:**

- Imagem `python:3.10-slim` (menor footprint)
- `PYTHONDONTWRITEBYTECODE=1` (sem .pyc)
- `PYTHONUNBUFFERED=1` (logs em tempo real)
- Cache de camada Docker (requirements primeiro)
- `--no-cache-dir` no pip (menor imagem)

## 4. Docker (Apenas API)

```bash
docker build -t datathon-passos-magicos .
docker run -d -p 8000:8000 --name datathon-api datathon-passos-magicos
```

## 5. Execução Local (Sem Docker)

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate          # Linux/Mac
# .venv\Scripts\activate           # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar testes
pytest tests/ -v --cov=app --cov=src --cov-report=term-missing

# Iniciar API
uvicorn app.main:app --reload --port 8000
```

## 6. URLs de Acesso

| Serviço    | URL                          | Credenciais         |
|------------|------------------------------|---------------------|
| API        | <http://localhost:8000>        | —                   |
| Frontend   | <http://localhost:8000/app>    | —                   |
| Swagger    | <http://localhost:8000/docs>   | —                   |
| ReDoc      | <http://localhost:8000/redoc>  | —                   |
| Prometheus | <http://localhost:9090>        | —                   |
| Grafana    | <http://localhost:3000>        | admin / admin       |
| Loki       | <http://localhost:3100>        | —                   |

## 7. Dependências Python (`requirements.txt`)

| Grupo            | Pacotes                                          |
|------------------|--------------------------------------------------|
| API              | fastapi ≥0.110, uvicorn ≥0.27, pydantic ≥2.0    |
| Core Data        | pandas ≥2.0, numpy ≥1.24                        |
| Machine Learning | scikit-learn ≥1.3, joblib ≥1.3                   |
| Observabilidade  | prometheus-fastapi-instrumentator ≥6.1           |
| Testes           | pytest ≥8.0, pytest-cov ≥4.1, httpx ≥0.27       |

---

*Anterior: [07 - Frontend](./07-FRONTEND.md) | Próximo: [Índice](./README.md)*
