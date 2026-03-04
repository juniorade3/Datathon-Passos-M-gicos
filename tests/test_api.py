"""
Testes unitários para a API FastAPI.

Utiliza TestClient do FastAPI e mock do modelo .joblib para testar
o endpoint /predict sem dependência do arquivo real do modelo.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app

# Cliente de testes
client = TestClient(app)


def _payload_valido() -> dict:
    """Retorna um payload de exemplo com todas as 9 features."""
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


def _mock_modelo():
    """Cria um mock do modelo com predict e predict_proba."""
    modelo = MagicMock()
    modelo.predict.return_value = np.array([1])
    modelo.predict_proba.return_value = np.array([[0.25, 0.75]])
    return modelo


class TestHealthCheck:
    """Testes do endpoint de health check."""

    def test_health_check_status_ok(self):
        """GET / deve retornar status 200."""
        resposta = client.get("/")
        assert resposta.status_code == 200

    def test_health_check_conteudo(self):
        """GET / deve retornar o campo 'status' com valor 'ok'."""
        resposta = client.get("/")
        dados = resposta.json()
        assert dados["status"] == "ok"


class TestEndpointPredict:
    """Testes do endpoint POST /predict."""

    @patch("app.routes.os.path.exists", return_value=True)
    @patch("app.routes.joblib.load")
    def test_previsao_com_risco(self, mock_load, mock_exists):
        """Deve retornar previsão 1 (Com Risco) quando o modelo prediz 1."""
        modelo_mock = _mock_modelo()
        modelo_mock.predict.return_value = np.array([1])
        modelo_mock.predict_proba.return_value = np.array([[0.25, 0.75]])
        mock_load.return_value = modelo_mock

        resposta = client.post("/predict", json=_payload_valido())

        assert resposta.status_code == 200
        dados = resposta.json()
        assert dados["previsao"] == 1
        assert dados["status"] == "Com Risco"
        assert dados["probabilidade_risco"] == 0.75

    @patch("app.routes.os.path.exists", return_value=True)
    @patch("app.routes.joblib.load")
    def test_previsao_sem_risco(self, mock_load, mock_exists):
        """Deve retornar previsão 0 (Sem Risco) quando o modelo prediz 0."""
        modelo_mock = _mock_modelo()
        modelo_mock.predict.return_value = np.array([0])
        modelo_mock.predict_proba.return_value = np.array([[0.85, 0.15]])
        mock_load.return_value = modelo_mock

        resposta = client.post("/predict", json=_payload_valido())

        assert resposta.status_code == 200
        dados = resposta.json()
        assert dados["previsao"] == 0
        assert dados["status"] == "Sem Risco"
        assert dados["probabilidade_risco"] == 0.15

    @patch("app.routes.os.path.exists", return_value=True)
    @patch("app.routes.joblib.load")
    def test_resposta_contem_campos_esperados(self, mock_load, mock_exists):
        """A resposta deve conter os campos: previsao, status, probabilidade_risco."""
        mock_load.return_value = _mock_modelo()

        resposta = client.post("/predict", json=_payload_valido())
        dados = resposta.json()

        assert "previsao" in dados
        assert "status" in dados
        assert "probabilidade_risco" in dados

    def test_payload_incompleto_retorna_422(self):
        """Payload sem campos obrigatórios deve retornar HTTP 422."""
        payload_incompleto = {"Idade": 14.0, "IAA": 7.5}
        resposta = client.post("/predict", json=payload_incompleto)
        assert resposta.status_code == 422

    def test_payload_vazio_retorna_422(self):
        """Payload vazio deve retornar HTTP 422."""
        resposta = client.post("/predict", json={})
        assert resposta.status_code == 422

    @patch("app.routes.os.path.exists", return_value=False)
    def test_modelo_nao_encontrado_retorna_503(self, mock_exists):
        """Se o modelo não existir, deve retornar HTTP 503."""
        resposta = client.post("/predict", json=_payload_valido())
        assert resposta.status_code == 503

    @patch("app.routes.os.path.exists", return_value=True)
    @patch("app.routes.joblib.load")
    def test_probabilidade_entre_0_e_1(self, mock_load, mock_exists):
        """A probabilidade de risco deve estar entre 0 e 1."""
        mock_load.return_value = _mock_modelo()

        resposta = client.post("/predict", json=_payload_valido())
        dados = resposta.json()

        assert 0 <= dados["probabilidade_risco"] <= 1
