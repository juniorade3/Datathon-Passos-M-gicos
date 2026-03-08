# 🧠 Pipeline de Machine Learning

## 1. Visão Geral do Pipeline

```
┌───────────┐    ┌────────────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────┐
│  Dataset  │──▶ │ Pré-processam. │──▶ │ Treinamento  │──▶ │ Avaliação  │──▶ │ Deploy   │
│  PEDE     │    │ (preprocessing)│    │ (train.py)   │    │ (evaluate) │    │ (.joblib) │
│  .xlsx    │    │                │    │              │    │            │    │          │
└───────────┘    └────────────────┘    └──────────────┘    └────────────┘    └──────────┘
```

## 2. Pré-processamento (`src/preprocessing.py`)

### Função Principal

```python
def preparar_dados(dados: dict) -> pd.DataFrame
```

**Responsabilidades:**

1. **Validação de campos:** verifica se todas as 9 features obrigatórias estão
   presentes no dicionário de entrada
2. **Ordenação de colunas:** cria um DataFrame com as colunas na ordem exata
   esperada pelo modelo
3. **Conversão de tipos:** converte todos os valores para `float64` para
   garantir consistência numérica

**Features esperadas (constante `FEATURES_ESPERADAS`):**

```python
FEATURES_ESPERADAS = [
    "Idade", "Ano ingresso", "IAA", "IEG",
    "IPS", "IDA", "IPV", "Mat", "Por"
]
```

**Tratamento de erros:**

- Se alguma feature estiver ausente, a função levanta `ValueError` com a lista
  dos campos faltantes:

  ```
  ValueError: Campos obrigatórios ausentes: ['Idade', 'IEG']
  ```

- Campos extras no dicionário são ignorados silenciosamente

**Fluxo dentro da API:**

```
JSON do usuário  →  model_dump(by_alias=True)  →  preparar_dados()  →  DataFrame  →  modelo.predict()
```

### Pré-processamento no Notebook

No notebook exploratório (`notebook/datathon.ipynb`), o pré-processamento é
mais extenso e inclui:

- **Carregamento** do arquivo Excel (PEDE 2022, 2023, 2024) via `pandas.read_excel()`
- **Limpeza** de registros com valores nulos nas features selecionadas
- **Criação da variável-alvo** (`target`): variável binária calculada
  comparando a fase/série do aluno com a fase ideal para a idade:
  - `0` = Sem Risco (aluno na fase ideal ou adiantado)
  - `1` = Com Risco (aluno com defasagem escolar)
- **Seleção das 9 features** mais relevantes
- **Conversão de tipos** para `float`

## 3. Treinamento (`src/train.py`)

### Funções Disponíveis

#### `treinar_modelo()`

```python
def treinar_modelo(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 100,
    random_state: int = 42,
    **kwargs,
) -> RandomForestClassifier
```

**Algoritmo:** `RandomForestClassifier` (scikit-learn)

**Configuração padrão:**

| Parâmetro        | Valor         | Justificativa                                         |
|------------------|---------------|-------------------------------------------------------|
| `n_estimators`   | 100           | Boa relação custo-benefício para tamanhos moderados   |
| `class_weight`   | `"balanced"`  | Compensar desbalanceamento das classes                |
| `random_state`   | 42            | Garantir reprodutibilidade dos resultados             |

**Por que Random Forest?**

- **Robustez:** resistente a overfitting, especialmente com `n_estimators=100`
- **Interpretabilidade:** permite extrair feature importances
- **Sem normalização:** não requer escalonamento das features
- **Balanceamento:** `class_weight='balanced'` ajusta os pesos
  proporcionalmente à frequência inversa das classes, lidando com desbalanceamento
- **Generalização:** funciona bem com dados tabulares de tamanho moderado

**Divisão dos dados (no notebook):**

- 80% treino / 20% teste
- `random_state=42` para reprodutibilidade
- `train_test_split` do scikit-learn

#### `salvar_modelo()`

```python
def salvar_modelo(modelo: RandomForestClassifier, caminho: str) -> None
```

Salva o modelo treinado em disco usando `joblib`:

- Cria o diretório automaticamente se não existir (`os.makedirs`)
- Formato: `.joblib` (mais eficiente que pickle para arrays NumPy)

#### `carregar_modelo()`

```python
def carregar_modelo(caminho: str) -> RandomForestClassifier
```

Carrega um modelo previamente salvo do disco.

## 4. Avaliação (`src/evaluate.py`)

### Função Principal

```python
def avaliar_modelo(
    modelo,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict
```

**Métricas calculadas:**

| Métrica                   | Descrição                                                       |
|---------------------------|-----------------------------------------------------------------|
| `acuracia`                | Proporção de predições corretas (todas as classes)              |
| `f1_score`                | F1-Score ponderado (weighted), equilibra precision e recall     |
| `classification_report`   | Relatório detalhado por classe (Sem Risco / Com Risco)          |

**Por que F1-Score weighted?**

- Em datasets desbalanceados, a acurácia pode ser enganosa
- O F1 pondera precision e recall, fornecendo uma visão mais realista
- O modo `weighted` considera o tamanho de cada classe

**Formato do retorno:**

```python
{
    "acuracia": 0.85,
    "f1_score": 0.84,
    "classification_report": """
              precision    recall  f1-score   support

   Sem Risco       0.87      0.90      0.88       120
   Com Risco       0.82      0.78      0.80        80

    accuracy                           0.85       200
   macro avg       0.85      0.84      0.84       200
weighted avg       0.85      0.85      0.85       200
"""
}
```

## 5. Modelo Serializado

**Arquivo:** `modelos/modelo_risco_defasagem.joblib`  
**Tamanho:** ~3.8 MB  
**Formato:** joblib (pickle otimizado para NumPy)

**Carregamento na API:**

```python
# app/routes.py
modelo = joblib.load(CAMINHO_MODELO)
previsao = modelo.predict(df_entrada)
probabilidades = modelo.predict_proba(df_entrada)
```

> **Nota:** O modelo é carregado a cada request em `POST /predict`. Em
> cenários de alta carga, considerar carregar na inicialização da aplicação
> (startup event) para melhor performance.

## 6. Engenharia de Features

O modelo utiliza as **9 features originais** da Pesquisa PEDE sem features
derivadas adicionais. Os indicadores (IAA, IEG, IPS, IDA, IPV) já foram
engenheirados pela própria pesquisa e representam dimensões avaliativas
compostas do aluno:

```
Dados brutos PEDE  →  Indicadores compostos  →  Features do modelo
   (questionários)     (IAA, IEG, IPS,           (9 variáveis numéricas)
                        IDA, IPV)
```

## 7. Possíveis Melhorias Futuras

| Melhoria                          | Benefício Esperado                              |
|-----------------------------------|-------------------------------------------------|
| Carregar modelo no startup        | Reduzir latência de predição                    |
| Hyperparameter tuning (GridSearch)| Potencial ganho de performance                  |
| Cross-validation (k-fold)        | Avaliação mais robusta do modelo                |
| Feature engineering adicional     | Capturar relações não-lineares entre indicadores|
| SHAP values                      | Explicabilidade individual das predições        |
| Modelos alternativos (XGBoost)   | Potencial ganho de accuracy                     |
| Versionamento de modelos (MLflow)| Rastreabilidade e reprodutibilidade              |

---

*Anterior: [03 - API Reference](./03-API-REFERENCE.md) | Próximo: [05 - Testes](./05-TESTES.md)*
