# 📘 Visão Geral do Projeto

## 1. Contexto

A **Associação Passos Mágicos** é uma organização sem fins lucrativos que atua
na transformação da vida de crianças e jovens em situação de vulnerabilidade
social por meio da educação. A ONG aplica periodicamente a **Pesquisa PEDE**
(Pesquisa Extensiva do Desenvolvimento Educacional), que captura indicadores
educacionais e socioeconômicos dos alunos atendidos.

A **defasagem escolar** — quando o aluno se encontra em uma série abaixo da
esperada para sua idade — é um dos principais indicadores de risco educacional.
Identificar precocemente alunos propensos a essa situação permite que a
instituição intervenha com programas de reforço, acompanhamento psicossocial e
outras ações direcionadas.

## 2. Objetivo do Projeto

Desenvolver um **modelo preditivo de Machine Learning** capaz de estimar o
**risco de defasagem escolar** de estudantes, utilizando os indicadores da
Pesquisa PEDE (anos 2022, 2023 e 2024). O projeto contempla todo o ciclo de
vida do modelo:

1. **Exploração e análise dos dados** (notebook exploratório)
2. **Pré-processamento e engenharia de features**
3. **Treinamento e validação do modelo**
4. **Deploy via API REST** acessível por uma interface web
5. **Monitoramento contínuo** com stack de observabilidade

## 3. Variável-Alvo (Target)

A variável alvo é binária e representa o risco de defasagem escolar:

| Valor | Significado                                        |
|-------|----------------------------------------------------|
| `0`   | **Sem Risco** — aluno na fase ideal ou adiantado   |
| `1`   | **Com Risco** — aluno apresenta defasagem escolar  |

A variável é calculada comparando a fase/série atual do aluno com a fase ideal
esperada para a sua idade, conforme definido pela Pesquisa PEDE.

## 4. Features do Modelo

O modelo utiliza **9 variáveis preditoras** extraídas da Pesquisa PEDE:

| Feature          | Descrição                                | Tipo    | Range Típico  |
|------------------|------------------------------------------|---------|---------------|
| `Idade`          | Idade do aluno em anos                   | Inteiro | 5 – 25        |
| `Ano ingresso`   | Ano em que o aluno ingressou na ONG      | Inteiro | 2000 – 2030   |
| `IAA`            | Indicador de Auto Avaliação              | Float   | 0 – 10        |
| `IEG`            | Indicador de Engajamento                 | Float   | 0 – 10        |
| `IPS`            | Indicador Psicossocial                   | Float   | 0 – 10        |
| `IDA`            | Indicador de Desempenho Acadêmico        | Float   | 0 – 10        |
| `IPV`            | Indicador do Ponto de Virada             | Float   | 0 – 10        |
| `Mat`            | Nota de Matemática                       | Float   | 0 – 10        |
| `Por`            | Nota de Português                        | Float   | 0 – 10        |

### Descrição dos Indicadores PEDE

- **IAA (Indicador de Auto Avaliação):** mede a percepção do aluno sobre seu
  próprio desempenho e capacidade educacional.
- **IEG (Indicador de Engajamento):** avalia o nível de participação e
  engajamento do aluno nas atividades da ONG.
- **IPS (Indicador Psicossocial):** captura aspectos psicossociais que impactam
  o desenvolvimento educacional do aluno.
- **IDA (Indicador de Desempenho Acadêmico):** reflete o desempenho acadêmico
  geral do aluno.
- **IPV (Indicador do Ponto de Virada):** indica o momento de transformação na
  trajetória educacional do aluno.

## 5. Stack Tecnológica

| Camada            | Tecnologia                                               |
|-------------------|----------------------------------------------------------|
| Linguagem         | Python 3.10+                                             |
| Machine Learning  | scikit-learn, pandas, NumPy                               |
| API               | FastAPI + Uvicorn                                         |
| Serialização      | joblib (`.joblib`)                                        |
| Validação         | Pydantic v2                                               |
| Testes            | pytest + pytest-cov + httpx                               |
| Containerização   | Docker + Docker Compose                                   |
| Observabilidade   | Prometheus + Grafana + Loki + Promtail                    |
| Frontend          | HTML5, CSS3 (Vanilla), JavaScript (ES6+)                  |
| Logging           | JSON estruturado (stdout)                                 |

## 6. Resumo da Solução

```
┌────────────────────────────────────────────────────────────────┐
│                     SOLUÇÃO COMPLETA                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────────┐ │
│  │ Dataset  │──▶│ Pipeline │──▶│ Modelo   │──▶│ API REST   │ │
│  │ PEDE     │   │ ML       │   │ .joblib  │   │ FastAPI    │ │
│  └──────────┘   └──────────┘   └──────────┘   └─────┬──────┘ │
│                                                      │        │
│       ┌──────────────────────────────────────────────┤        │
│       │                                              │        │
│       ▼                                              ▼        │
│  ┌──────────┐   ┌──────────┐              ┌──────────────┐   │
│  │ Frontend │   │ Testes   │              │ Observability │   │
│  │ HTML/CSS │   │ pytest   │              │ Prom+Graf+Lok│   │
│  └──────────┘   └──────────┘              └──────────────┘   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

*Próximo: [02 - Arquitetura do Projeto](./02-ARQUITETURA.md)*
