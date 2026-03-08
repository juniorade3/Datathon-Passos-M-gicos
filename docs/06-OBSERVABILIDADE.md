# 📊 Observabilidade

## 1. Visão Geral

O projeto implementa um stack completo de observabilidade para monitoramento
em tempo real da API e do modelo de Machine Learning:

```
                          ┌─────────────────────────────────────────┐
                          │           OBSERVABILIDADE               │
                          ├─────────────────────────────────────────┤
                          │                                         │
                          │  ┌─────────┐  ┌──────┐  ┌──────────┐  │
                          │  │Prometheus│  │ Loki │  │ Promtail │  │
                          │  │(métricas)│  │(logs)│  │(coletor) │  │
                          │  └────┬─────┘  └──┬───┘  └──────────┘  │
                          │       │           │                     │
                          │       └─────┬─────┘                    │
                          │             │                           │
                          │       ┌─────▼─────┐                    │
                          │       │  Grafana   │                    │
                          │       │(dashboards)│                    │
                          │       └───────────┘                    │
                          │                                         │
                          └─────────────────────────────────────────┘
```

### Stack

| Componente | Porta  | Função                                        |
|------------|--------|-----------------------------------------------|
| Prometheus | `:9090`| Coleta e armazenamento de métricas time-series |
| Grafana    | `:3000`| Visualização de dashboards (login: `admin`/`admin`) |
| Loki       | `:3100`| Agregação e consulta de logs                   |
| Promtail   | —      | Coleta de logs dos containers → Loki           |

## 2. Prometheus

### Configuração (`observability/prometheus.yml`)

```yaml
global:
  scrape_interval: 5s       # Frequência de coleta de métricas
  evaluation_interval: 5s   # Frequência de avaliação de regras

scrape_configs:
  - job_name: "passos-magicos-api"
    metrics_path: /metrics            # Endpoint exposto pela API
    static_configs:
      - targets: ["api:8000"]         # Nome do serviço no Docker Compose
        labels:
          app: "passos-magicos"
          environment: "production"
```

### Métricas Coletadas

#### Métricas HTTP (via `prometheus-fastapi-instrumentator`)

| Métrica                                    | Tipo      | Descrição                              |
|--------------------------------------------|-----------|----------------------------------------|
| `http_requests_total`                      | Counter   | Total de requests HTTP por método/rota/status |
| `http_request_duration_seconds_bucket`     | Histogram | Distribuição de latência por percentil  |
| `http_request_size_bytes`                 | Summary   | Tamanho das requisições                 |
| `http_response_size_bytes`               | Summary   | Tamanho das respostas                   |

#### Métricas Customizadas de Drift (via `prometheus_client`)

| Métrica                            | Tipo  | Labels     | Descrição                                       |
|------------------------------------|-------|------------|--------------------------------------------------|
| `drift_total_predicoes`            | Gauge | —          | Nº de predições no buffer circular               |
| `drift_taxa_risco`                 | Gauge | —          | Proporção de predições "Com Risco"              |
| `drift_probabilidade_media`        | Gauge | —          | Média da probabilidade de risco                  |
| `drift_feature_media`              | Gauge | `feature`  | Média de cada feature nas últimas predições      |
| `drift_feature_std`                | Gauge | `feature`  | Desvio padrão de cada feature                    |

### Acessando o Prometheus

```bash
# UI Web
http://localhost:9090

# Exemplo de query PromQL
rate(http_requests_total{handler="/predict"}[5m])
```

## 3. Grafana

### Acesso

| Item       | Valor                        |
|------------|------------------------------|
| URL        | `http://localhost:3000`      |
| Usuário    | `admin`                      |
| Senha      | `admin`                      |
| Sign up    | Desabilitado                 |

### Datasources Auto-Provisionados

Configurados em `observability/grafana/provisioning/datasources/datasources.yml`:

| Datasource | Tipo       | URL Interna           | Default |
|------------|------------|-----------------------|---------|
| Prometheus | prometheus | `http://prometheus:9090` | ✅ Sim  |
| Loki       | loki       | `http://loki:3100`     | Não     |

### Dashboard: "Passos Mágicos — Monitoramento"

Provisionado automaticamente em `observability/grafana/dashboards/api_monitoring.json`.

#### Seção 1: 📊 Métricas da API

| Painel                          | Tipo       | Query PromQL                                                    |
|---------------------------------|------------|-----------------------------------------------------------------|
| Requests por Segundo            | Timeseries | `rate(http_requests_total{...}[1m])`                            |
| Latência p50/p95/p99            | Timeseries | `histogram_quantile(0.50/0.95/0.99, rate(http_request_duration_seconds_bucket{...}[1m]))` |
| Taxa de Erros (HTTP 4xx/5xx)    | Timeseries | `rate(http_requests_total{status=~"4..\|5.."}[1m])`            |

#### Seção 2: 🤖 Drift do Modelo

| Painel                            | Tipo       | Métrica                        |
|-----------------------------------|------------|--------------------------------|
| Taxa de Risco                     | Gauge      | `drift_taxa_risco`             |
| Probabilidade Média de Risco      | Gauge      | `drift_probabilidade_media`    |
| Total de Predições no Buffer      | Stat       | `drift_total_predicoes`        |
| Taxa de Risco ao Longo do Tempo   | Timeseries | `drift_taxa_risco`             |
| Média das Features (Drift)        | Timeseries | `drift_feature_media`          |
| Desvio Padrão das Features        | Timeseries | `drift_feature_std`            |

Os painéis gauge possuem **thresholds de alertia visual:**

| Cor     | Range Risco | Significado                |
|---------|-------------|----------------------------|
| 🟢 Verde  | 0 – 0.3    | Normal                     |
| 🟡 Amarelo | 0.3 – 0.5  | Atenção                    |
| 🟠 Laranja | 0.5 – 0.7  | Alerta                     |
| 🔴 Vermelho | 0.7 – 1.0  | Drift significativo         |

#### Seção 3: 📝 Logs da API

| Painel              | Tipo | Query LogQL                                  |
|---------------------|------|----------------------------------------------|
| Logs em Tempo Real  | Logs | `{job="docker"} \|= "passos_magicos"`        |

## 4. Loki + Promtail

### Loki

Loki é o sistema de agregação de logs (análogo ao Elasticsearch, mas otimizado
para logs). Roda com a configuração padrão (`local-config.yaml`) no container.

### Promtail (`observability/promtail.yml`)

Promtail é o agente que coleta logs dos containers Docker e envia para o Loki.

```yaml
server:
  http_listen_port: 9080

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    static_configs:
      - targets: [localhost]
        labels:
          job: docker
          __path__: /var/lib/docker/containers/**/*.log
    pipeline_stages:
      - json:                    # Parse do formato JSON do Docker
          expressions:
            log: log
            stream: stream
            time: time
      - labels:
          stream:                # Adiciona label stream (stdout/stderr)
      - output:
          source: log            # Extrai o campo log como mensagem
```

**Volumes montados no Promtail:**

- `/var/lib/docker/containers:/var/lib/docker/containers:ro` — acesso aos logs dos containers
- `/var/log:/var/log:ro` — acesso a logs do sistema (opcional)

## 5. Logging Estruturado

A API emite logs em formato **JSON estruturado** para facilitar parsing por
Promtail/Loki:

```python
# app/main.py
LOG_FORMAT = (
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
    '"logger": "%(name)s", "message": "%(message)s"}'
)
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)
```

**Exemplo de log emitido em cada predição:**

```json
{
  "timestamp": "2024-03-08 13:00:00,123",
  "level": "INFO",
  "logger": "passos_magicos",
  "message": "Predição realizada: previsao=0 status=Sem Risco prob_risco=0.4581 features={...}"
}
```

## 6. Monitoramento de Drift (`app/drift.py`)

### O que é Model Drift?

**Model drift** (ou concept drift) ocorre quando a distribuição dos dados de
produção diverge da distribuição dos dados de treinamento, degradando a
performance do modelo ao longo do tempo.

### Implementação

O módulo `app/drift.py` implementa um **buffer circular** thread-safe:

```python
MAX_REGISTROS = 1000                          # Tamanho máximo do buffer
_historico: deque[dict] = deque(maxlen=1000)  # Descarta os mais antigos
_lock = threading.Lock()                       # Thread safety
```

**Fluxo:**

1. Cada predição em `POST /predict` chama `registrar_predicao()`
2. Os dados (features + previsão + probabilidade) são adicionados ao buffer
3. As métricas Prometheus são recalculadas (média, std, taxa de risco por feature)
4. O endpoint `GET /drift` retorna as estatísticas atuais

### Métricas Monitoradas

| Indicador                    | O que detecta                                     |
|------------------------------|---------------------------------------------------|
| Taxa de risco                | Mudança na distribuição do target                  |
| Probabilidade média/std      | Mudança na confiança do modelo                     |
| Média/std de cada feature    | Data drift (mudança na distribuição das features)  |

### Interpretando os Dados de Drift

- **Taxa de risco estável:** modelo recebendo dados similares ao treino ✅
- **Taxa de risco subindo/descendo abruptamente:** possível drift ⚠️
- **Desvio padrão de features crescendo:** maior variabilidade nos dados ⚠️
- **Média de features muito diferente do treino:** data drift confirmado 🚨

## 7. Docker Compose — Serviços de Observabilidade

```yaml
# docker-compose.yml (resumo dos serviços de observabilidade)

prometheus:
  image: prom/prometheus:latest
  ports: ["9090:9090"]
  volumes:
    - ./observability/prometheus.yml:/etc/prometheus/prometheus.yml:ro
  command:
    - "--storage.tsdb.retention.time=7d"    # Retenção de 7 dias
  depends_on: api (service_healthy)

loki:
  image: grafana/loki:latest
  ports: ["3100:3100"]

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
  depends_on: loki

grafana:
  image: grafana/grafana:latest
  ports: ["3000:3000"]
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_USERS_ALLOW_SIGN_UP=false
  depends_on: prometheus, loki
```

**Rede:** Todos os serviços compartilham a rede `observability` (bridge).

**Volumes persistentes:**

- `prometheus_data` — métricas do Prometheus (retenção: 7 dias)
- `loki_data` — logs do Loki
- `grafana_data` — configurações e state do Grafana

---

*Anterior: [05 - Testes](./05-TESTES.md) | Próximo: [07 - Frontend](./07-FRONTEND.md)*
