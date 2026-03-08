# 📡 Referência da API

## Informações Gerais

| Item             | Valor                                              |
|------------------|----------------------------------------------------|
| **Base URL**     | `http://localhost:8000`                             |
| **Protocolo**    | HTTP/1.1                                            |
| **Content-Type** | `application/json`                                  |
| **Framework**    | FastAPI 0.110+                                      |
| **Swagger UI**   | `http://localhost:8000/docs`                        |
| **ReDoc**        | `http://localhost:8000/redoc`                       |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json`                |

---

## Endpoints

### `GET /` — Health Check

Verifica se a API está no ar e funcionando.

**Request:**

```bash
curl http://localhost:8000/
```

**Response (200 OK):**

```json
{
  "status": "ok",
  "mensagem": "API Passos Mágicos está funcionando!"
}
```

| Campo      | Tipo   | Descrição                          |
|------------|--------|------------------------------------|
| `status`   | string | Sempre `"ok"` se a API está saudável |
| `mensagem` | string | Mensagem descritiva                |

---

### `POST /predict` — Predição de Risco

Recebe os dados de um aluno e retorna a predição de risco de defasagem escolar.

**Headers:**

```
Content-Type: application/json
```

**Request Body (JSON):**

| Campo           | Tipo  | Obrigatório | Descrição                          | Range     |
|-----------------|-------|-------------|------------------------------------|-----------|
| `Idade`         | float | ✅ Sim      | Idade do aluno em anos             | 5 – 25    |
| `Ano ingresso`  | float | ✅ Sim      | Ano de ingresso na ONG             | 2000 – 2030 |
| `IAA`           | float | ✅ Sim      | Indicador de Auto Avaliação        | 0 – 10    |
| `IEG`           | float | ✅ Sim      | Indicador de Engajamento           | 0 – 10    |
| `IPS`           | float | ✅ Sim      | Indicador Psicossocial             | 0 – 10    |
| `IDA`           | float | ✅ Sim      | Indicador de Desempenho Acadêmico  | 0 – 10    |
| `IPV`           | float | ✅ Sim      | Indicador do Ponto de Virada       | 0 – 10    |
| `Mat`           | float | ✅ Sim      | Nota de Matemática                 | 0 – 10    |
| `Por`           | float | ✅ Sim      | Nota de Português                  | 0 – 10    |

> **Nota:** O campo `Ano ingresso` utiliza alias do Pydantic. No JSON, deve ser
> enviado como `"Ano ingresso"` (com espaço).

**Exemplo de Request:**

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Idade": 14,
    "Ano ingresso": 2020,
    "IAA": 7.5,
    "IEG": 6.8,
    "IPS": 8.0,
    "IDA": 7.2,
    "IPV": 5.5,
    "Mat": 8.0,
    "Por": 7.0
  }'
```

**Response (200 OK):**

```json
{
  "previsao": 0,
  "status": "Sem Risco",
  "probabilidade_risco": 0.4581
}
```

| Campo                  | Tipo   | Descrição                                     |
|------------------------|--------|-----------------------------------------------|
| `previsao`             | int    | `0` = Sem Risco, `1` = Com Risco              |
| `status`               | string | `"Sem Risco"` ou `"Com Risco"`                |
| `probabilidade_risco`  | float  | Probabilidade (0 a 1) de o aluno estar em risco |

#### Respostas de Erro

**422 Unprocessable Entity** — Campos obrigatórios ausentes ou inválidos:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "IAA"],
      "msg": "Field required",
      "input": { "Idade": 14.0 }
    }
  ]
}
```

**503 Service Unavailable** — Arquivo do modelo não encontrado:

```json
{
  "detail": "Modelo não encontrado. Verifique o arquivo .joblib."
}
```

---

### `GET /drift` — Monitoramento de Drift

Retorna estatísticas das últimas predições armazenadas no buffer circular,
úteis para detectar mudanças na distribuição dos dados (data drift).

**Request:**

```bash
curl http://localhost:8000/drift
```

**Response (200 OK) — Com predições registradas:**

```json
{
  "total_predicoes": 5,
  "taxa_risco": 0.2,
  "probabilidade_media_risco": 0.4823,
  "probabilidade_std_risco": 0.0712,
  "features": {
    "Idade": {
      "media": 13.6,
      "std": 1.02,
      "min": 12.0,
      "max": 15.0
    },
    "Ano ingresso": {
      "media": 2019.8,
      "std": 1.47,
      "min": 2018.0,
      "max": 2022.0
    },
    "IAA": {
      "media": 7.1,
      "std": 0.85,
      "min": 5.5,
      "max": 8.0
    }
  }
}
```

| Campo                        | Tipo   | Descrição                                              |
|------------------------------|--------|--------------------------------------------------------|
| `total_predicoes`            | int    | Total de predições no buffer (máximo 1000)             |
| `taxa_risco`                 | float  | Proporção de predições classificadas como "Com Risco" |
| `probabilidade_media_risco`  | float  | Média da probabilidade de risco                        |
| `probabilidade_std_risco`    | float  | Desvio padrão da probabilidade de risco                |
| `features`                   | object | Estatísticas descritivas de cada feature               |
| `features.<nome>.media`      | float  | Média da feature                                       |
| `features.<nome>.std`        | float  | Desvio padrão da feature                               |
| `features.<nome>.min`        | float  | Valor mínimo da feature                                |
| `features.<nome>.max`        | float  | Valor máximo da feature                                |

**Response (200 OK) — Sem predições registradas:**

```json
{
  "total_predicoes": 0,
  "mensagem": "Nenhuma predição registrada ainda."
}
```

---

### `GET /metrics` — Métricas Prometheus

Expõe métricas no formato Prometheus para scrape. Gerado automaticamente pelo
`prometheus-fastapi-instrumentator`.

**Request:**

```bash
curl http://localhost:8000/metrics
```

**Response (200 OK) — text/plain:**

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{handler="/predict",method="POST",status="200"} 42.0
...
# HELP drift_taxa_risco Proporção de predições classificadas como 'Com Risco'
# TYPE drift_taxa_risco gauge
drift_taxa_risco 0.2
...
```

**Métricas Customizadas de Drift:**

| Métrica                         | Tipo  | Descrição                                          |
|---------------------------------|-------|----------------------------------------------------|
| `drift_total_predicoes`         | Gauge | Total de predições no buffer                       |
| `drift_taxa_risco`              | Gauge | Proporção de risco nas predições                   |
| `drift_probabilidade_media`     | Gauge | Probabilidade média de risco                       |
| `drift_feature_media{feature=}` | Gauge | Média de cada feature nas predições                |
| `drift_feature_std{feature=}`   | Gauge | Desvio padrão de cada feature nas predições        |

---

### `GET /app` — Frontend Web

Serve a página HTML principal do frontend. O frontend e seus assets estáticos
(CSS, JS) são servidos diretamente pela API.

| Rota          | Descrição                          |
|---------------|------------------------------------|
| `/app`        | Página principal (index.html)      |
| `/static/*`   | Assets estáticos (CSS, JS)         |

---

## Schemas Pydantic

### `AlunoInput` (Entrada)

```python
class AlunoInput(BaseModel):
    Idade: float
    Ano_ingresso: float  # alias: "Ano ingresso"
    IAA: float
    IEG: float
    IPS: float
    IDA: float
    IPV: float
    Mat: float
    Por: float

    model_config = {"populate_by_name": True}
```

### `PrevisaoOutput` (Saída)

```python
class PrevisaoOutput(BaseModel):
    previsao: int         # 0 = Sem Risco, 1 = Com Risco
    status: str           # Descrição textual
    probabilidade_risco: float  # 0.0 a 1.0
```

---

## CORS

A API permite chamadas de qualquer origem (configuração de desenvolvimento):

```python
CORSMiddleware(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> ⚠️ **Atenção:** Em produção, restrinja `allow_origins` apenas ao domínio do
> frontend.

---

*Anterior: [02 - Arquitetura](./02-ARQUITETURA.md) | Próximo: [04 - Pipeline de ML](./04-PIPELINE-ML.md)*
