"""
Módulo de pré-processamento dos dados de entrada da API.

Responsável por receber os dados brutos (dicionário/JSON) enviados pelo
usuário e transformá-los em um DataFrame pandas pronto para ser consumido
pelo modelo de Machine Learning.
"""

import pandas as pd


# Features esperadas pelo modelo, na ordem correta
FEATURES_ESPERADAS: list[str] = [
    "Idade",
    "Ano ingresso",
    "IAA",
    "IEG",
    "IPS",
    "IDA",
    "IPV",
    "Mat",
    "Por",
]


def preparar_dados(dados: dict) -> pd.DataFrame:
    """
    Recebe um dicionário com os dados de um aluno e retorna um DataFrame
    pandas com as colunas na ordem esperada pelo modelo.

    Parâmetros
    ----------
    dados : dict
        Dicionário contendo as 9 features do aluno.
        Exemplo: {"Idade": 14, "Ano ingresso": 2020, "IAA": 7.5, ...}

    Retorna
    -------
    pd.DataFrame
        DataFrame com uma linha e as 9 colunas ordenadas.

    Levanta
    -------
    ValueError
        Se alguma feature obrigatória estiver ausente no dicionário.
    """
    # Verificar se todas as features obrigatórias estão presentes
    campos_ausentes = [f for f in FEATURES_ESPERADAS if f not in dados]
    if campos_ausentes:
        raise ValueError(
            f"Campos obrigatórios ausentes: {campos_ausentes}"
        )

    # Criar DataFrame garantindo a ordem das colunas
    df = pd.DataFrame([dados], columns=FEATURES_ESPERADAS)

    # Converter todas as colunas para float (garantir consistência numérica)
    df = df.astype(float)

    return df