"""
Módulo de treinamento do modelo de Machine Learning.

Contém funções genéricas para treinar um RandomForestClassifier e
salvar/carregar o modelo treinado via joblib.
"""

import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def treinar_modelo(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_estimators: int = 100,
    random_state: int = 42,
    **kwargs,
) -> RandomForestClassifier:
    """
    Treina um RandomForestClassifier com class_weight='balanced'.

    Parâmetros
    ----------
    X_train : pd.DataFrame
        Features de treino.
    y_train : pd.Series
        Variável alvo de treino.
    n_estimators : int, default=100
        Número de árvores na floresta.
    random_state : int, default=42
        Semente para reprodutibilidade.
    **kwargs
        Parâmetros adicionais passados ao RandomForestClassifier.

    Retorna
    -------
    RandomForestClassifier
        Modelo treinado.
    """
    modelo = RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight="balanced",
        random_state=random_state,
        **kwargs,
    )
    modelo.fit(X_train, y_train)
    return modelo


def salvar_modelo(modelo: RandomForestClassifier, caminho: str) -> None:
    """
    Salva o modelo treinado em disco usando joblib.

    Parâmetros
    ----------
    modelo : RandomForestClassifier
        Modelo treinado a ser salvo.
    caminho : str
        Caminho completo do arquivo de saída (ex: 'modelos/modelo.joblib').
    """
    # Criar diretório caso não exista
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    joblib.dump(modelo, caminho)


def carregar_modelo(caminho: str) -> RandomForestClassifier:
    """
    Carrega um modelo previamente salvo com joblib.

    Parâmetros
    ----------
    caminho : str
        Caminho do arquivo .joblib.

    Retorna
    -------
    RandomForestClassifier
        Modelo carregado.
    """
    return joblib.load(caminho)
