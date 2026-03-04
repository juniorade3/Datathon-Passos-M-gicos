"""
Testes unitários para os módulos src/train.py e src/evaluate.py.

Valida o treinamento do modelo RandomForest, funções de salvar/carregar
e a avaliação com métricas.
"""

import os
import tempfile

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from src.evaluate import avaliar_modelo
from src.train import carregar_modelo, salvar_modelo, treinar_modelo


# =====================================================================
#  Fixtures auxiliares
# =====================================================================

def _dados_treino():
    """Cria dados sintéticos de treino."""
    np.random.seed(42)
    X = pd.DataFrame({
        "feat1": np.random.rand(50),
        "feat2": np.random.rand(50),
    })
    y = pd.Series(np.random.randint(0, 2, 50))
    return X, y


# =====================================================================
#  Testes do módulo train.py
# =====================================================================

class TestTreinarModelo:
    """Testes para a função treinar_modelo."""

    def test_retorna_random_forest(self):
        """Deve retornar uma instância de RandomForestClassifier."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        assert isinstance(modelo, RandomForestClassifier)

    def test_class_weight_balanced(self):
        """O modelo deve usar class_weight='balanced'."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        assert modelo.class_weight == "balanced"

    def test_modelo_consegue_predizer(self):
        """O modelo treinado deve ser capaz de fazer predições."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        previsoes = modelo.predict(X)
        assert len(previsoes) == len(y)

    def test_parametros_customizados(self):
        """Deve aceitar parâmetros customizados."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y, n_estimators=10, max_depth=3)
        assert modelo.n_estimators == 10
        assert modelo.max_depth == 3


class TestSalvarCarregarModelo:
    """Testes para salvar e carregar modelos."""

    def test_salvar_e_carregar(self):
        """Deve salvar e carregar o modelo preservando funcionalidade."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y, n_estimators=5)

        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = os.path.join(tmpdir, "modelo_test.joblib")
            salvar_modelo(modelo, caminho)

            assert os.path.exists(caminho)

            modelo_carregado = carregar_modelo(caminho)
            assert isinstance(modelo_carregado, RandomForestClassifier)

            # Predições devem ser idênticas
            pred_original = modelo.predict(X)
            pred_carregado = modelo_carregado.predict(X)
            np.testing.assert_array_equal(pred_original, pred_carregado)


# =====================================================================
#  Testes do módulo evaluate.py
# =====================================================================

class TestAvaliarModelo:
    """Testes para a função avaliar_modelo."""

    def test_retorna_dicionario(self):
        """Deve retornar um dicionário."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        resultado = avaliar_modelo(modelo, X, y)
        assert isinstance(resultado, dict)

    def test_contem_chaves_esperadas(self):
        """Deve conter acuracia, f1_score e classification_report."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        resultado = avaliar_modelo(modelo, X, y)
        assert "acuracia" in resultado
        assert "f1_score" in resultado
        assert "classification_report" in resultado

    def test_acuracia_entre_0_e_1(self):
        """A acurácia deve estar entre 0 e 1."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        resultado = avaliar_modelo(modelo, X, y)
        assert 0 <= resultado["acuracia"] <= 1

    def test_f1_entre_0_e_1(self):
        """O F1-Score deve estar entre 0 e 1."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        resultado = avaliar_modelo(modelo, X, y)
        assert 0 <= resultado["f1_score"] <= 1

    def test_report_eh_string(self):
        """O classification_report deve ser uma string."""
        X, y = _dados_treino()
        modelo = treinar_modelo(X, y)
        resultado = avaliar_modelo(modelo, X, y)
        assert isinstance(resultado["classification_report"], str)
