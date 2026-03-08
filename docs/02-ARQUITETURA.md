# 🏗️ Arquitetura do Projeto

## 1. Estrutura de Diretórios

```
datathon-passos-magicos/
│
├── app/                                  # 🔌 Aplicação FastAPI (camada de API)
│   ├── __init__.py                       #    Marca o diretório como pacote Python
│   ├── main.py                           #    Ponto de entrada: CORS, Prometheus, static files
│   ├── routes.py                         #    Rotas: POST /predict, schemas Pydantic
│   └── drift.py                          #    Monitoramento de drift: GET /drift, buffer circular
│
├── src/                                  # 🧠 Pipeline de Machine Learning
│   ├── __init__.py                       #    Marca o diretório como pacote Python
│   ├── preprocessing.py                  #    Pré-processamento: validação e formatação dos dados
│   ├── train.py                          #    Treinamento: RandomForest + salvar/carregar modelo
│   └── evaluate.py                       #    Avaliação: Acurácia, F1-Score, Classification Report
│
├── modelos/                              # 💾 Modelo treinado serializado
│   └── modelo_risco_defasagem.joblib     #    Modelo RandomForest salvo com joblib (~3.8 MB)
│
├── tests/                                # 🧪 Testes automatizados (pytest)
│   ├── __init__.py
│   ├── test_api.py                       #    9 testes: health check, predição, validação, erros
│   ├── test_preprocessing.py             #    8 testes: validação de dados, tipos, campos
│   └── test_train_evaluate.py            #    10 testes: treino, salvar/carregar, métricas
│
├── frontend/                             # 🎨 Interface web do modelo
│   ├── index.html                        #    Página única (SPA): formulário + monitoramento
│   ├── style.css                         #    Tema escuro premium com glassmorphism
│   └── app.js                            #    Lógica JS: chamadas à API, renderização dinâmica
│
├── observability/                        # 📊 Stack de observabilidade
│   ├── prometheus.yml                    #    Config de scrape do Prometheus (intervalo 5s)
│   ├── promtail.yml                      #    Coleta de logs Docker → Loki
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/
│       │   │   └── datasources.yml       #    Prometheus + Loki como datasources
│       │   └── dashboards/
│       │       └── dashboards.yml        #    Provisioning automático de dashboards
│       └── dashboards/
│           └── api_monitoring.json       #    Dashboard: Métricas API + Drift + Logs
│
├── notebook/                             # 📓 Análise exploratória
│   └── datathon.ipynb                    #    Notebook Jupyter: EDA + treinamento do modelo
│
├── data/                                 # 📂 Dados brutos
│   └── BASE DE DADOS PEDE 2024 - DATATHON.xlsx
│
├── docs/                                 # 📘 Documentação do projeto (você está aqui)
│
├── Dockerfile                            #    Imagem Docker da aplicação (python:3.10-slim)
├── docker-compose.yml                    #    Orquestração: 6 serviços (API, testes, observabilidade)
├── requirements.txt                      #    Dependências Python do projeto
├── .gitignore                            #    Arquivos ignorados pelo Git
└── README.md                             #    Documentação principal do projeto
```

## 2. Diagrama de Componentes

```
                            ┌─────────────────────────────────────────┐
                            │           Docker Compose                │
                            │        (docker-compose.yml)             │
                            └──────────┬──────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
   ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────────┐
   │   API FastAPI    │    │  Testes (pytest)  │    │   Observabilidade    │
   │   (container)    │    │   (container)     │    │   (3 containers)     │
   │                  │    │                   │    │                      │
   │ ┌──────────────┐ │    │ test_api.py       │    │ ┌──────────────────┐ │
   │ │  main.py     │ │    │ test_preproc.py   │    │ │   Prometheus     │ │
   │ │  (FastAPI)   │ │    │ test_train_eval.py│    │ │   :9090          │ │
   │ └──┬───────┬───┘ │    └──────────────────┘    │ └────────┬─────────┘ │
   │    │       │      │                            │          │           │
   │    ▼       ▼      │                            │          ▼           │
   │ ┌──────┐ ┌─────┐ │                            │ ┌──────────────────┐ │
   │ │routes│ │drift│ │                            │ │    Grafana       │ │
   │ │ .py  │ │ .py │ │                            │ │    :3000         │ │
   │ └──┬───┘ └──┬──┘ │                            │ └────────▲─────────┘ │
   │    │        │     │                            │          │           │
   │    ▼        │     │                            │ ┌────────┴─────────┐ │
   │ ┌──────────┐│     │                            │ │  Loki + Promtail │ │
   │ │   src/   ││     │                            │ │  :3100           │ │
   │ │ ML Pipe  ││     │                            │ └──────────────────┘ │
   │ └──────────┘│     │                            └──────────────────────┘
   │    │        │     │
   │    ▼        │     │
   │ ┌──────────────┐ │
   │ │   modelo     │ │
   │ │  .joblib     │ │
   │ └──────────────┘ │
   │                   │
   │ ┌──────────────┐ │
   │ │  frontend/   │ │
   │ │  (static)    │ │
   │ └──────────────┘ │
   │   :8000           │
   └─────────────────┘
```

## 3. Fluxo de Dados

### 3.1 Fluxo de Predição

```
Usuário (Frontend/Swagger/cURL)
    │
    │  POST /predict  { Idade, Ano ingresso, IAA, IEG, IPS, IDA, IPV, Mat, Por }
    ▼
┌──────────────────────────┐
│  app/routes.py           │
│  ├─ Validação Pydantic   │  ◄── AlunoInput (9 campos obrigatórios, tipo float)
│  ├─ Carregar modelo      │  ◄── joblib.load(modelo_risco_defasagem.joblib)
│  ├─ Preparar dados       │  ◄── src/preprocessing.py → DataFrame ordenado
│  ├─ model.predict()      │  ◄── RandomForestClassifier
│  ├─ model.predict_proba()│
│  ├─ Log JSON estruturado │  ──▶ stdout → Promtail → Loki
│  └─ Registrar no drift   │  ──▶ app/drift.py (buffer circular)
└──────────────────────────┘
    │
    │  Resposta JSON: { previsao: 0|1, status: "...", probabilidade_risco: 0.xxxx }
    ▼
Usuário
```

### 3.2 Fluxo de Monitoramento

```
┌─────────────┐  scrape /metrics (5s)  ┌────────────┐
│  API :8000  │ ◄──────────────────────│ Prometheus │
│             │                        │   :9090    │
│ ┌─────────┐ │                        └──────┬─────┘
│ │ /drift  │ │                               │ datasource
│ │ buffer  │ │                               ▼
│ │ circular│ │                        ┌────────────┐
│ └─────────┘ │                        │  Grafana   │
│             │                        │   :3000    │
│  stdout log │                        └──────▲─────┘
│  (JSON)     │                               │ datasource
└──────┬──────┘                        ┌──────┴─────┐
       │                               │    Loki    │
       ▼                               │   :3100    │
┌────────────┐   push logs             └──────▲─────┘
│  Promtail  │ ────────────────────────────────┘
│  (sidecar) │
└────────────┘
```

### 3.3 Fluxo de Testes

```
docker compose up → container "tests"
    │
    │ depends_on: api (service_healthy)
    ▼
pytest tests/ -v --cov=app --cov=src
    │
    ├── test_api.py ──────────────── TestClient (FastAPI) + mocks do modelo
    ├── test_preprocessing.py ────── Testa função preparar_dados()
    └── test_train_evaluate.py ───── Testa treinar, salvar, carregar, avaliar
    │
    ▼
Relatório de cobertura (term-missing)
```

## 4. Separação de Responsabilidades

| Camada          | Diretório     | Responsabilidade                                          |
|-----------------|---------------|-----------------------------------------------------------|
| **API**         | `app/`        | Receber requests, validar, servir predições, expor métricas |
| **ML Pipeline** | `src/`        | Lógica de pré-processamento, treinamento e avaliação       |
| **Modelo**      | `modelos/`    | Armazenamento do artefato treinado (serializado)           |
| **Testes**      | `tests/`      | Validação automatizada de todos os módulos                  |
| **Frontend**    | `frontend/`   | Interface visual para interação com a API                   |
| **Observab.**   | `observability/` | Configuração da stack de monitoramento                   |
| **Dados**       | `data/`       | Dataset original (Excel)                                    |
| **Exploração**  | `notebook/`   | Notebook Jupyter para análise exploratória                  |

## 5. Decisões Arquiteturais

### Por que FastAPI?

- Framework moderno e de alta performance para Python
- Validação automática com Pydantic
- Documentação Swagger/OpenAPI automática
- Suporte nativo a async (embora a API use sync por simplicidade)

### Por que Random Forest?

- Robusto para datasets tabulares de tamanho moderado
- Interpretável (feature importances)
- Lida bem com desbalanceamento de classes via `class_weight='balanced'`
- Não requer normalização/padronização de features

### Por que Docker Compose?

- Reprodutibilidade: mesmo ambiente em qualquer máquina
- Orquestração simplificada de 6 serviços interdependentes
- Execução de testes automatizada no deploy
- Stack de observabilidade autocontida

### Por que buffer circular para drift?

- Solução leve, in-memory, sem dependência de banco de dados
- Thread-safe com lock
- Tamanho fixo (1000 registros) — sem crescimento ilimitado
- Exporta métricas diretamente para o Prometheus

---

*Anterior: [01 - Visão Geral](./01-VISAO-GERAL.md) | Próximo: [03 - API Reference](./03-API-REFERENCE.md)*
