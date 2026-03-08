# 🧪 Testes Automatizados

## 1. Visão Geral

O projeto conta com **27 testes automatizados** organizados em 3 módulos de
teste, cobrindo todas as camadas da aplicação:

| Módulo                      | Nº Testes | Camada Testada              |
|-----------------------------|-----------|-----------------------------|
| `tests/test_api.py`        | 9         | API FastAPI (endpoints)     |
| `tests/test_preprocessing.py` | 8      | Pré-processamento de dados  |
| `tests/test_train_evaluate.py` | 10    | Treinamento e avaliação ML  |

### Bibliotecas Utilizadas

| Biblioteca    | Versão  | Função                                        |
|---------------|---------|-----------------------------------------------|
| `pytest`      | ≥ 8.0   | Framework de testes                            |
| `pytest-cov`  | ≥ 4.1   | Cobertura de código                            |
| `httpx`       | ≥ 0.27  | Client HTTP assíncrono (dependência do TestClient) |
| `unittest.mock` | stdlib | Mocking de dependências externas (modelo)     |

## 2. Executando os Testes

### Localmente

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Rodar todos os testes com cobertura
pytest tests/ -v --cov=app --cov=src --cov-report=term-missing

# Rodar um módulo específico
pytest tests/test_api.py -v

# Rodar um teste específico
pytest tests/test_api.py::TestEndpointPredict::test_previsao_com_risco -v

# Gerar relatório HTML de cobertura
pytest tests/ --cov=app --cov=src --cov-report=html
```

### Via Docker Compose

```bash
# Subir tudo (testes rodam automaticamente após API ficar saudável)
docker compose up -d --build

# Ver resultados dos testes
docker compose logs tests

# Rodar testes sob demanda
docker compose run --rm tests pytest tests/ -v
```

O container `tests` depende do health check da API (`service_healthy`) e
executa uma única vez, reportando os resultados.

## 3. Detalhamento dos Testes

### 3.1 — `tests/test_api.py` (9 testes)

Testa a API FastAPI usando `TestClient` com **mocks do modelo** (não depende
do arquivo `.joblib` real).

#### Classe `TestHealthCheck` (2 testes)

| Teste                           | Descrição                                    |
|---------------------------------|----------------------------------------------|
| `test_health_check_status_ok`   | `GET /` retorna status HTTP 200              |
| `test_health_check_conteudo`    | `GET /` retorna `"status": "ok"` no body     |

#### Classe `TestEndpointPredict` (7 testes)

| Teste                                    | Descrição                                                 |
|------------------------------------------|-----------------------------------------------------------|
| `test_previsao_com_risco`                | Modelo retorna classe 1 → response "Com Risco" + prob 0.75 |
| `test_previsao_sem_risco`                | Modelo retorna classe 0 → response "Sem Risco" + prob 0.15 |
| `test_resposta_contem_campos_esperados`  | Verifica presença dos campos: previsao, status, probabilidade_risco |
| `test_payload_incompleto_retorna_422`    | Payload com apenas 2 campos → HTTP 422                     |
| `test_payload_vazio_retorna_422`         | Payload `{}` → HTTP 422                                    |
| `test_modelo_nao_encontrado_retorna_503` | Arquivo .joblib não existe → HTTP 503                      |
| `test_probabilidade_entre_0_e_1`         | Verifica que probabilidade está no range [0, 1]            |

**Estratégia de Mock:**

```python
@patch("app.routes.os.path.exists", return_value=True)
@patch("app.routes.joblib.load")
def test_previsao_com_risco(self, mock_load, mock_exists):
    modelo_mock = MagicMock()
    modelo_mock.predict.return_value = np.array([1])
    modelo_mock.predict_proba.return_value = np.array([[0.25, 0.75]])
    mock_load.return_value = modelo_mock
    # ...
```

Os testes usam `unittest.mock.patch` para:

- Simular existência do arquivo do modelo (`os.path.exists`)
- Substituir `joblib.load` por um mock com `predict()` e `predict_proba()` controlados

### 3.2 — `tests/test_preprocessing.py` (8 testes)

Testa a função `preparar_dados()` do módulo `src/preprocessing.py`.

#### Classe `TestPrepararDados` (8 testes)

| Teste                              | Descrição                                              |
|------------------------------------|--------------------------------------------------------|
| `test_retorna_dataframe`           | Input válido → retorna `pd.DataFrame`                  |
| `test_dataframe_uma_linha`         | DataFrame retornado tem exatamente 1 linha             |
| `test_colunas_corretas`            | Colunas correspondem a `FEATURES_ESPERADAS` (9 cols)   |
| `test_valores_corretos`            | Valores no DataFrame correspondem ao input             |
| `test_tipos_float`                 | Todas as colunas são `float64` (mesmo com input int)   |
| `test_campo_ausente_levanta_erro`  | Feature faltante → `ValueError`                        |
| `test_multiplos_campos_ausentes`   | Múltiplas features faltantes → `ValueError` com lista  |
| `test_campo_extra_ignorado`        | Campo extra no input → ignorado, colunas corretas      |

### 3.3 — `tests/test_train_evaluate.py` (10 testes)

Testa os módulos `src/train.py` e `src/evaluate.py` com dados sintéticos.

#### Classe `TestTreinarModelo` (4 testes)

| Teste                          | Descrição                                           |
|--------------------------------|-----------------------------------------------------|
| `test_retorna_random_forest`   | Retorna instância de `RandomForestClassifier`       |
| `test_class_weight_balanced`   | Verifica que `class_weight='balanced'`              |
| `test_modelo_consegue_predizer`| Modelo treinado faz predições com mesmo nº de saídas|
| `test_parametros_customizados` | Aceita `n_estimators=10, max_depth=3`               |

#### Classe `TestSalvarCarregarModelo` (1 teste)

| Teste                    | Descrição                                                     |
|--------------------------|---------------------------------------------------------------|
| `test_salvar_e_carregar` | Salva modelo → carrega → verifica predições idênticas         |

Usa `tempfile.TemporaryDirectory()` para não criar arquivos permanentes.

#### Classe `TestAvaliarModelo` (5 testes)

| Teste                          | Descrição                                    |
|--------------------------------|----------------------------------------------|
| `test_retorna_dicionario`      | Retorna `dict`                               |
| `test_contem_chaves_esperadas` | Dict contém: acuracia, f1_score, classification_report |
| `test_acuracia_entre_0_e_1`    | Acurácia no range [0, 1]                     |
| `test_f1_entre_0_e_1`          | F1-Score no range [0, 1]                     |
| `test_report_eh_string`        | Classification report é string               |

## 4. Cobertura de Código

Os testes cobrem os seguintes módulos:

| Módulo               | Cobertura Alvo |
|----------------------|----------------|
| `app/main.py`        | ✅             |
| `app/routes.py`      | ✅             |
| `app/drift.py`       | ✅             |
| `src/preprocessing.py`| ✅            |
| `src/train.py`       | ✅             |
| `src/evaluate.py`    | ✅             |

Comando de cobertura com relatório detalhado:

```bash
pytest tests/ -v --cov=app --cov=src --cov-report=term-missing
```

## 5. Boas Práticas Aplicadas

| Prática                        | Implementação                                    |
|--------------------------------|--------------------------------------------------|
| **Isolamento**                 | Mocks para modelo .joblib (testes não dependem do arquivo real) |
| **Dados Sintéticos**           | Dados de treino gerados com `np.random` (reprodutíveis com seed 42) |
| **Arquivos Temporários**       | Uso de `tempfile.TemporaryDirectory()` para salvar/carregar modelos |
| **Organização em Classes**     | Testes agrupados por funcionalidade (`TestHealthCheck`, `TestEndpointPredict`, etc.) |
| **Validação de Contrato**      | Verificação de tipos, campos de resposta e ranges de valores |
| **Testes de Erro**             | Payloads inválidos, modelo ausente, campos faltantes |
| **CI-ready**                   | Testes executam automaticamente via Docker Compose |

---

*Anterior: [04 - Pipeline de ML](./04-PIPELINE-ML.md) | Próximo: [06 - Observabilidade](./06-OBSERVABILIDADE.md)*
