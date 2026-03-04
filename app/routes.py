"""
Definição das rotas e schemas da API.

Contém o endpoint POST /predict para realizar predições de risco de
defasagem escolar, além dos schemas Pydantic para validação de
entrada e saída.
"""

import logging
import os

import joblib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.drift import registrar_predicao
from src.preprocessing import preparar_dados

logger = logging.getLogger("passos_magicos")

# Roteador da API
router = APIRouter()

# Caminho do modelo treinado
CAMINHO_MODELO = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "modelos",
    "modelo_risco_defasagem.joblib",
)


# =====================================================================
#  Schemas Pydantic
# =====================================================================

class AlunoInput(BaseModel):
    """Schema de entrada com as 9 features do aluno."""

    Idade: float = Field(..., description="Idade do aluno em anos")
    Ano_ingresso: float = Field(
        ..., alias="Ano ingresso", description="Ano de ingresso na ONG"
    )
    IAA: float = Field(
        ..., description="Indicador de Auto Avaliação"
    )
    IEG: float = Field(
        ..., description="Indicador de Engajamento"
    )
    IPS: float = Field(
        ..., description="Indicador Psicossocial"
    )
    IDA: float = Field(
        ..., description="Indicador de Desempenho Acadêmico"
    )
    IPV: float = Field(
        ..., description="Indicador do Ponto de Virada"
    )
    Mat: float = Field(
        ..., description="Nota de Matemática"
    )
    Por: float = Field(
        ..., description="Nota de Português"
    )

    model_config = {"populate_by_name": True}


class PrevisaoOutput(BaseModel):
    """Schema de saída com o resultado da predição."""

    previsao: int = Field(
        ..., description="0 = Sem Risco, 1 = Com Risco"
    )
    status: str = Field(
        ..., description="Descrição textual do resultado"
    )
    probabilidade_risco: float = Field(
        ..., description="Probabilidade de o aluno estar em risco (0 a 1)"
    )


# =====================================================================
#  Endpoint de predição
# =====================================================================

@router.post(
    "/predict",
    response_model=PrevisaoOutput,
    tags=["Predição"],
    summary="Prever risco de defasagem escolar",
)
def prever_risco(aluno: AlunoInput):
    """
    Recebe os dados de um aluno e retorna a previsão de risco de
    defasagem escolar com a probabilidade associada.
    """
    # Verificar se o arquivo do modelo existe
    if not os.path.exists(CAMINHO_MODELO):
        logger.error("Modelo não encontrado em %s", CAMINHO_MODELO)
        raise HTTPException(
            status_code=503,
            detail="Modelo não encontrado. Verifique o arquivo .joblib.",
        )

    # Carregar o modelo
    modelo = joblib.load(CAMINHO_MODELO)

    # Preparar dados de entrada (converter para DataFrame)
    dados_dict = aluno.model_dump(by_alias=True)
    df_entrada = preparar_dados(dados_dict)

    # Realizar a predição
    previsao = int(modelo.predict(df_entrada)[0])
    probabilidades = modelo.predict_proba(df_entrada)[0]

    # Probabilidade da classe 1 (Com Risco)
    probabilidade_risco = float(probabilidades[1])

    # Determinar status textual
    status_texto = "Com Risco" if previsao == 1 else "Sem Risco"

    # Log estruturado da predição
    logger.info(
        "Predição realizada: previsao=%d status=%s prob_risco=%.4f features=%s",
        previsao,
        status_texto,
        probabilidade_risco,
        dados_dict,
    )

    # Registrar no buffer de drift
    registrar_predicao(
        features=dados_dict,
        previsao=previsao,
        probabilidade_risco=probabilidade_risco,
    )

    return PrevisaoOutput(
        previsao=previsao,
        status=status_texto,
        probabilidade_risco=round(probabilidade_risco, 4),
    )
