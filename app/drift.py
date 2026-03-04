"""
Módulo de monitoramento de drift do modelo.

Mantém um buffer circular em memória com as últimas predições e
expõe um endpoint GET /drift com estatísticas para detecção de
mudanças na distribuição das features e da saída do modelo.
"""

import threading
from collections import deque
from typing import Any

import numpy as np
from fastapi import APIRouter
from prometheus_client import Gauge

from src.preprocessing import FEATURES_ESPERADAS

# =====================================================================
#  Configuração
# =====================================================================

MAX_REGISTROS = 1000  # Tamanho do buffer circular

# Buffer thread-safe para armazenar predições recentes
_lock = threading.Lock()
_historico: deque[dict[str, Any]] = deque(maxlen=MAX_REGISTROS)

# =====================================================================
#  Métricas Prometheus para drift
# =====================================================================

drift_total_predicoes = Gauge(
    "drift_total_predicoes",
    "Total de predições registradas no buffer de drift",
)

drift_taxa_risco = Gauge(
    "drift_taxa_risco",
    "Proporção de predições classificadas como 'Com Risco'",
)

drift_probabilidade_media = Gauge(
    "drift_probabilidade_media",
    "Probabilidade média de risco nas últimas predições",
)

drift_feature_media = Gauge(
    "drift_feature_media",
    "Média de cada feature nas últimas predições",
    ["feature"],
)

drift_feature_std = Gauge(
    "drift_feature_std",
    "Desvio padrão de cada feature nas últimas predições",
    ["feature"],
)


# =====================================================================
#  Funções de registro
# =====================================================================

def registrar_predicao(
    features: dict[str, float],
    previsao: int,
    probabilidade_risco: float,
) -> None:
    """Registra uma predição no buffer e atualiza métricas Prometheus."""
    registro = {
        "features": features,
        "previsao": previsao,
        "probabilidade_risco": probabilidade_risco,
    }

    with _lock:
        _historico.append(registro)
        _atualizar_metricas()


def _atualizar_metricas() -> None:
    """Recalcula as métricas Prometheus com base no buffer atual."""
    if not _historico:
        return

    total = len(_historico)
    drift_total_predicoes.set(total)

    # Taxa de risco
    risco_count = sum(1 for r in _historico if r["previsao"] == 1)
    drift_taxa_risco.set(risco_count / total)

    # Probabilidade média
    probs = [r["probabilidade_risco"] for r in _historico]
    drift_probabilidade_media.set(float(np.mean(probs)))

    # Estatísticas por feature
    for feat in FEATURES_ESPERADAS:
        valores = [r["features"].get(feat, 0) for r in _historico]
        drift_feature_media.labels(feature=feat).set(float(np.mean(valores)))
        drift_feature_std.labels(feature=feat).set(float(np.std(valores)))


def _obter_estatisticas() -> dict[str, Any]:
    """Retorna um dicionário com as estatísticas atuais do buffer."""
    with _lock:
        if not _historico:
            return {
                "total_predicoes": 0,
                "mensagem": "Nenhuma predição registrada ainda.",
            }

        total = len(_historico)
        risco_count = sum(1 for r in _historico if r["previsao"] == 1)
        probs = [r["probabilidade_risco"] for r in _historico]

        # Estatísticas por feature
        features_stats = {}
        for feat in FEATURES_ESPERADAS:
            valores = [r["features"].get(feat, 0) for r in _historico]
            features_stats[feat] = {
                "media": round(float(np.mean(valores)), 4),
                "std": round(float(np.std(valores)), 4),
                "min": round(float(np.min(valores)), 4),
                "max": round(float(np.max(valores)), 4),
            }

        return {
            "total_predicoes": total,
            "taxa_risco": round(risco_count / total, 4),
            "probabilidade_media_risco": round(float(np.mean(probs)), 4),
            "probabilidade_std_risco": round(float(np.std(probs)), 4),
            "features": features_stats,
        }


# =====================================================================
#  Roteador
# =====================================================================

drift_router = APIRouter()


@drift_router.get(
    "/drift",
    tags=["Monitoramento"],
    summary="Estatísticas de drift do modelo",
)
def get_drift():
    """
    Retorna estatísticas das últimas predições para monitoramento
    de drift: distribuição das features, taxa de risco e
    probabilidade média.
    """
    return _obter_estatisticas()
