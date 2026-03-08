# 📘 Documentação do Projeto — Datathon Passos Mágicos

## Índice

Documentação completa do projeto de predição de risco de defasagem escolar
para a Associação Passos Mágicos.

| #  | Documento                                         | Descrição                                          |
|----|---------------------------------------------------|----------------------------------------------------|
| 01 | [Visão Geral](./01-VISAO-GERAL.md)               | Contexto, objetivo, variável-alvo, features, stack |
| 02 | [Arquitetura](./02-ARQUITETURA.md)                | Estrutura de diretórios, componentes, fluxo de dados |
| 03 | [Referência da API](./03-API-REFERENCE.md)        | Endpoints, schemas, exemplos, códigos de erro      |
| 04 | [Pipeline de ML](./04-PIPELINE-ML.md)             | Pré-processamento, treinamento, avaliação, modelo  |
| 05 | [Testes](./05-TESTES.md)                          | Catálogo de testes, cobertura, como executar        |
| 06 | [Observabilidade](./06-OBSERVABILIDADE.md)        | Prometheus, Grafana, Loki, drift monitoring         |
| 07 | [Frontend](./07-FRONTEND.md)                      | Design system, componentes, integração com API      |
| 08 | [Deploy](./08-DEPLOY.md)                          | Docker Compose, Dockerfile, execução local          |

---

## Quick Start

```bash
# Clone o repositório
git clone https://github.com/juniorade3/Datathon-Passos-M-gicos.git
cd Datathon-Passos-M-gicos

# Suba todos os serviços
docker compose up -d --build

# Acesse
# API:        http://localhost:8000
# Frontend:   http://localhost:8000/app
# Swagger:    http://localhost:8000/docs
# Grafana:    http://localhost:3000 (admin/admin)
```

---

## Sobre o Projeto

**Datathon Passos Mágicos** — Projeto acadêmico da Pós-Tech FIAP (Fase 5).

Modelo preditivo de Machine Learning para estimar o risco de defasagem
escolar de estudantes da Associação Passos Mágicos, servido por uma API
REST com monitoramento completo de observabilidade.

### Tecnologias Principais

- 🐍 Python 3.10+ | scikit-learn | FastAPI
- 🐳 Docker + Docker Compose
- 📊 Prometheus + Grafana + Loki
- 🧪 pytest (27 testes automatizados)
- 🎨 Frontend HTML/CSS/JS com tema escuro premium
