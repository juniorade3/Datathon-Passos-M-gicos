# 🌟 Datathon Passos Mágicos — Modelo Preditivo de Defasagem Escolar

Modelo preditivo para estimar o risco de defasagem escolar de estudantes
atendidos pela [Associação Passos Mágicos](https://passosmagicos.org.br/),
servido por uma **API REST** construída com **FastAPI** e monitorado por
um stack completo de **observabilidade** (Prometheus, Grafana, Loki).

---

## 📋 1) Visão Geral do Projeto

### Objetivo

Desenvolver um modelo de Machine Learning capaz de **prever o risco de
defasagem escolar** de estudantes atendidos pela Associação Passos Mágicos,
utilizando indicadores educacionais e socioeconômicos da Pesquisa PEDE.

A defasagem escolar ocorre quando o aluno está em uma série abaixo da
esperada para a sua idade, indicando atraso no percurso educacional.

### Variável Alvo

| Valor | Significado                                   |
|-------|-----------------------------------------------|
| `0`   | **Sem Risco** — aluno na fase ideal ou adiantado |
| `1`   | **Com Risco** — aluno com defasagem escolar      |

### Solução Proposta

Construção de uma **pipeline completa de Machine Learning**, desde o
pré-processamento dos dados até o deploy do modelo em produção via API:

1. **Modelo preditivo** treinado com `RandomForestClassifier` (scikit-learn),
   utilizando `class_weight='balanced'` para lidar com desbalanceamento de classes.
2. **API REST** (FastAPI) que recebe os dados de um aluno e retorna a
   previsão de risco, status textual e probabilidade.
3. **Frontend web** (HTML/CSS/JS) para interação visual com o modelo.
4. **Containerização** com Docker e **Docker Compose** para deploy completo.
5. **Monitoramento contínuo** com Prometheus (métricas), Grafana (dashboards),
   Loki + Promtail (logs) e endpoint de **drift do modelo**.

### Features do Modelo

| Feature        | Descrição                         |
|----------------|-----------------------------------|
| `Idade`        | Idade do aluno em anos            |
| `Ano ingresso` | Ano de ingresso na ONG            |
| `IAA`          | Indicador de Auto Avaliação       |
| `IEG`          | Indicador de Engajamento          |
| `IPS`          | Indicador Psicossocial            |
| `IDA`          | Indicador de Desempenho Acadêmico |
| `IPV`          | Indicador do Ponto de Virada      |
| `Mat`          | Nota de Matemática                |
| `Por`          | Nota de Português                 |

### Stack Tecnológica

| Camada         | Tecnologia                                     |
|----------------|-------------------------------------------------|
| Linguagem      | Python 3.10+                                    |
| Frameworks ML  | scikit-learn, pandas, NumPy                     |
| API            | FastAPI + Uvicorn                               |
| Serialização   | joblib (`.joblib`)                              |
| Validação      | Pydantic v2                                     |
| Testes         | pytest + pytest-cov + httpx                     |
| Empacotamento  | Docker + Docker Compose                         |
| Deploy         | Local (Docker Compose)                          |
| Monitoramento  | Logging estruturado (JSON) + Prometheus + Grafana (dashboard de drift) |
| Frontend       | HTML, CSS, JavaScript (puro)                    |

---

## 📁 2) Estrutura do Projeto (Diretórios e Arquivos)

```
datathon-passos-magicos/
├── app/                                  # Aplicação FastAPI
│   ├── __init__.py
│   ├── main.py                           # Inicialização, CORS, Prometheus, static files
│   ├── routes.py                         # Endpoint POST /predict + schemas Pydantic
│   └── drift.py                          # Monitoramento de drift + GET /drift
├── src/                                  # Pipeline de ML
│   ├── __init__.py
│   ├── preprocessing.py                  # Pré-processamento dos dados de entrada
│   ├── train.py                          # Treinamento do RandomForestClassifier
│   └── evaluate.py                       # Avaliação (Acurácia, F1, Classification Report)
├── modelos/
│   └── modelo_risco_defasagem.joblib     # Modelo treinado serializado com joblib
├── tests/                                # Testes automatizados
│   ├── __init__.py
│   ├── test_api.py                       # Testes da API (9 testes)
│   ├── test_preprocessing.py             # Testes de pré-processamento (8 testes)
│   └── test_train_evaluate.py            # Testes de treino e avaliação (10 testes)
├── frontend/                             # Interface web
│   ├── index.html                        # Página principal (formulário + drift)
│   ├── style.css                         # Tema escuro com glassmorphism
│   └── app.js                            # Integração com a API
├── observability/                        # Stack de observabilidade
│   ├── prometheus.yml                    # Configuração de scrape do Prometheus
│   ├── promtail.yml                      # Coleta de logs Docker → Loki
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/
│       │   │   └── datasources.yml       # Prometheus + Loki como datasources
│       │   └── dashboards/
│       │       └── dashboards.yml        # Provisioning automático de dashboards
│       └── dashboards/
│           └── api_monitoring.json       # Dashboard: API + Drift + Logs
├── notebook/
│   └── datathon.ipynb                    # Notebook exploratório e de treinamento
├── data/
│   └── BASE DE DADOS PEDE 2024 - DATATHON.xlsx  # Dataset original
├── Dockerfile                            # Imagem Docker da aplicação
├── docker-compose.yml                    # Stack completo (6 serviços)
├── requirements.txt                      # Dependências Python
└── README.md                             # Documentação do projeto
```

---

## 🚀 3) Instruções de Deploy

### Pré-requisitos

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Docker** + **Docker Compose** — [Download](https://www.docker.com/get-started)

### Docker Compose (recomendado) 🐳

Sobe a API, roda os testes automaticamente e inicia todo o stack de observabilidade:

```bash
# Buildar e subir todos os serviços
docker compose up -d --build

# Verificar os resultados dos testes
docker compose logs tests

# Parar todos os serviços
docker compose down
```

| Serviço        | URL                         | Descrição                           |
|----------------|-----------------------------|-------------------------------------|
| **API**        | <http://localhost:8000>       | FastAPI + `/metrics` + `/drift`     |
| **Frontend**   | <http://localhost:8000/app>   | Interface web do modelo             |
| **Swagger**    | <http://localhost:8000/docs>  | Documentação interativa da API      |
| **Prometheus** | <http://localhost:9090>       | Coleta de métricas (scrape 5s)      |
| **Grafana**    | <http://localhost:3000>       | Dashboards (login: `admin`/`admin`) |
| **Loki**       | <http://localhost:3100>       | Agregação de logs                   |

### Execução Local (sem Docker)

```bash
# Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar os testes
pytest tests/ -v --cov=app --cov=src --cov-report=term-missing

# Iniciar a API
uvicorn app.main:app --reload --port 8000
```

### Docker (apenas a API)

```bash
docker build -t datathon-passos-magicos .
docker run -d -p 8000:8000 --name datathon-api datathon-passos-magicos
```

---

## 📡 4) Exemplos de Chamadas à API

### Health Check

```bash
curl http://localhost:8000/
```

```json
{
  "status": "ok",
  "mensagem": "API Passos Mágicos está funcionando!"
}
```

### Predição de Risco

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

**Resposta:**

```json
{
  "previsao": 0,
  "status": "Sem Risco",
  "probabilidade_risco": 0.4581
}
```

### Monitoramento de Drift

```bash
curl http://localhost:8000/drift
```

**Resposta (exemplo com predições registradas):**

```json
{
  "total_predicoes": 5,
  "taxa_risco": 0.2,
  "probabilidade_media_risco": 0.4823,
  "probabilidade_std_risco": 0.0712,
  "features": {
    "Idade": { "media": 13.6, "std": 1.02, "min": 12.0, "max": 15.0 },
    "IAA": { "media": 7.1, "std": 0.85, "min": 5.5, "max": 8.0 }
  }
}
```

### Métricas Prometheus

```bash
curl http://localhost:8000/metrics
```

---

## 🔬 5) Etapas do Pipeline de Machine Learning

### 5.1 — Pré-processamento dos Dados

- **Carregamento**: leitura do arquivo Excel (PEDE 2022, 2023, 2024) via `pandas`
- **Limpeza**: remoção de registros com valores nulos nas features selecionadas
- **Criação da variável alvo**: variável binária de defasagem escolar (0 = Sem Risco, 1 = Com Risco), calculada comparando a fase/série do aluno com a fase ideal para a idade
- **Seleção de features**: escolha das 9 variáveis preditoras (Idade, Ano ingresso, IAA, IEG, IPS, IDA, IPV, Mat, Por)
- **Conversão de tipos**: todas as features convertidas para `float` para consistência numérica

Módulo: `src/preprocessing.py` — função `preparar_dados()` que recebe um dicionário e retorna um DataFrame padronizado.

### 5.2 — Engenharia de Features

- Não foram criadas features derivadas adicionais; o modelo utiliza as 9 features originais do dataset PEDE
- Os indicadores (IAA, IEG, IPS, IDA, IPV) já são features engenheiradas pela própria Pesquisa PEDE, representando dimensões avaliativas do aluno

### 5.3 — Treinamento e Validação

- **Divisão**: `train_test_split` com 80% treino / 20% teste (`random_state=42`)
- **Algoritmo**: `RandomForestClassifier` (scikit-learn)
- **Balanceamento**: `class_weight='balanced'` para compensar desbalanceamento entre classes
- **Hiperparâmetros**: `n_estimators=100`, `random_state=42`
- **Validação**: avaliação no conjunto de teste com Acurácia, F1-Score (weighted) e Classification Report

Módulo: `src/train.py` — função `treinar_modelo()`.

### 5.4 — Seleção de Modelo

- **Modelo escolhido**: Random Forest por ser robusto, interpretável (feature importances) e eficaz com datasets tabulares de tamanho moderado
- **Feature Importances**: análise da importância de cada variável para identificar os indicadores mais relevantes na predição de risco

### 5.5 — Serialização e Deploy

- **Serialização**: modelo salvo com `joblib` em `modelos/modelo_risco_defasagem.joblib`
- **Servindo**: API FastAPI carrega o modelo via `joblib.load()` e expõe o endpoint `POST /predict`
- **Containerização**: Dockerfile empacota a API + modelo para deploy reprodutível
- **Orquestração**: Docker Compose sobe toda a stack (API, testes, observabilidade)

Módulo: `src/train.py` — funções `salvar_modelo()` e `carregar_modelo()`.

### 5.6 — Monitoramento Contínuo (Pós-deploy)

- **Logging estruturado**: cada predição é logada em formato JSON (timestamp, features, resultado)
- **Métricas Prometheus**: requests/s, latência, taxa de erros via `prometheus-fastapi-instrumentator`
- **Dashboard de drift**: endpoint `GET /drift` e dashboard Grafana monitoram a distribuição das features e taxa de risco ao longo do tempo
- **Agregação de logs**: Loki + Promtail coletam e centralizam logs dos containers

Módulo: `app/drift.py` — buffer circular de predições com métricas Prometheus.

---

## 📈 Observabilidade

### Dashboard Grafana

O dashboard **"Passos Mágicos — Monitoramento"** é provisionado automaticamente e contém:

| Seção                   | Painéis                                                         |
|-------------------------|-----------------------------------------------------------------|
| **📊 Métricas da API** | Requests/s, Latência p50/p95/p99, Taxa de erros                |
| **🤖 Drift do Modelo** | Taxa de risco, Probabilidade média, Distribuição das features   |
| **📝 Logs**            | Logs em tempo real via Loki                                     |

### Arquitetura de Observabilidade

```
┌──────────┐    scrape /metrics     ┌────────────┐
│   API    │◄───────────────────────│ Prometheus │
│ FastAPI  │                        └─────┬──────┘
│ :8000    │                              │
└────┬─────┘                              │ datasource
     │ logs (stdout)                      ▼
     │                              ┌──────────┐
     ▼                              │ Grafana  │
┌──────────┐    push logs     ┌────►│  :3000   │
│ Promtail │─────────────────►│    └──────────┘
└──────────┘                  │ Loki
                              │ :3100
                              └──────┘
```

---

## 📊 Dataset

Pesquisa PEDE (Pesquisa Extensiva do Desenvolvimento Educacional),
anos 2022, 2023 e 2024. Dados anonimizados fornecidos pela Associação
Passos Mágicos para o Datathon.

---

## 📝 Licença

Projeto acadêmico — Pós Tech FIAP.
# Datathon-Passos-M-gicos
