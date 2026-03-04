"""
Módulo de avaliação do modelo de Machine Learning.

Contém funções para calcular métricas de desempenho do modelo treinado
(Acurácia, F1-Score e Classification Report).
"""

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)


def avaliar_modelo(
    modelo,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """
    Avalia o modelo nos dados de teste e retorna um dicionário com as
    principais métricas.

    Parâmetros
    ----------
    modelo : estimator
        Modelo treinado compatível com a interface do scikit-learn.
    X_test : pd.DataFrame
        Features de teste.
    y_test : pd.Series
        Variável alvo de teste.

    Retorna
    -------
    dict
        Dicionário contendo:
        - "acuracia": float
        - "f1_score": float
        - "classification_report": str (relatório detalhado)
    """
    y_pred = modelo.predict(X_test)

    acuracia = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    relatorio = classification_report(
        y_test,
        y_pred,
        target_names=["Sem Risco", "Com Risco"],
    )

    return {
        "acuracia": acuracia,
        "f1_score": f1,
        "classification_report": relatorio,
    }
