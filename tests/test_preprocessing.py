"""
Testes unitários para o módulo src/preprocessing.py.

Valida o comportamento da função preparar_dados() em cenários
de entrada válida e entrada com campos ausentes.
"""

import pandas as pd
import pytest

from src.preprocessing import FEATURES_ESPERADAS, preparar_dados


def _dados_validos() -> dict:
    """Retorna um dicionário de exemplo com todas as 9 features."""
    return {
        "Idade": 14.0,
        "Ano ingresso": 2020.0,
        "IAA": 7.5,
        "IEG": 6.8,
        "IPS": 8.0,
        "IDA": 7.2,
        "IPV": 5.5,
        "Mat": 8.0,
        "Por": 7.0,
    }


class TestPrepararDados:
    """Conjunto de testes para a função preparar_dados."""

    def test_retorna_dataframe(self):
        """Deve retornar um objeto do tipo pd.DataFrame."""
        resultado = preparar_dados(_dados_validos())
        assert isinstance(resultado, pd.DataFrame)

    def test_dataframe_uma_linha(self):
        """O DataFrame retornado deve conter exatamente uma linha."""
        resultado = preparar_dados(_dados_validos())
        assert len(resultado) == 1

    def test_colunas_corretas(self):
        """As colunas devem corresponder exatamente às features esperadas."""
        resultado = preparar_dados(_dados_validos())
        assert list(resultado.columns) == FEATURES_ESPERADAS

    def test_valores_corretos(self):
        """Os valores do DataFrame devem corresponder aos dados de entrada."""
        dados = _dados_validos()
        resultado = preparar_dados(dados)
        for coluna in FEATURES_ESPERADAS:
            assert resultado[coluna].iloc[0] == float(dados[coluna])

    def test_tipos_float(self):
        """Todas as colunas devem ser do tipo float."""
        dados = _dados_validos()
        # Passar inteiros para verificar a conversão
        dados["Idade"] = 14
        dados["Ano ingresso"] = 2020
        resultado = preparar_dados(dados)
        for coluna in FEATURES_ESPERADAS:
            assert resultado[coluna].dtype == "float64"

    def test_campo_ausente_levanta_erro(self):
        """Deve levantar ValueError se alguma feature estiver ausente."""
        dados = _dados_validos()
        del dados["Idade"]
        with pytest.raises(ValueError, match="Campos obrigatórios ausentes"):
            preparar_dados(dados)

    def test_multiplos_campos_ausentes(self):
        """Deve listar todos os campos ausentes na mensagem de erro."""
        dados = {"Idade": 14.0, "IAA": 7.5}
        with pytest.raises(ValueError, match="Campos obrigatórios ausentes"):
            preparar_dados(dados)

    def test_campo_extra_ignorado(self):
        """Campos extras no dicionário devem ser ignorados sem erro."""
        dados = _dados_validos()
        dados["campo_extra"] = 999
        resultado = preparar_dados(dados)
        assert "campo_extra" not in resultado.columns
        assert list(resultado.columns) == FEATURES_ESPERADAS
