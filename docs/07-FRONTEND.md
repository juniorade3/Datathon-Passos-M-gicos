# 🎨 Frontend

## 1. Visão Geral

SPA construída com HTML, CSS e JavaScript puro (vanilla). Duas abas:

1. **Predição** — formulário para prever risco de defasagem escolar
2. **Monitoramento** — estatísticas de drift do modelo

**URL:** `http://localhost:8000/app`

## 2. Arquivos

| Arquivo      | Tamanho  | Função                                      |
|--------------|----------|---------------------------------------------|
| `index.html` | 13.5 KB  | Estrutura HTML (formulário + monitoramento)  |
| `style.css`  | 15.0 KB  | Tema escuro premium com glassmorphism        |
| `app.js`     | 11.7 KB  | Lógica JS: chamadas à API, UI dinâmica       |

## 3. Design System

### Paleta de Cores

| Variável          | Valor            | Uso                     |
|-------------------|------------------|-------------------------|
| `--bg-primary`    | `#0a0e1a`        | Fundo principal         |
| `--accent`        | `#6366f1`        | Cor principal (indigo)  |
| `--success`       | `#10b981`        | Sem Risco (verde)       |
| `--danger`        | `#ef4444`        | Com Risco (vermelho)    |
| `--text-primary`  | `#f1f5f9`        | Texto principal         |

### Efeitos Visuais

- **Glassmorphism:** `backdrop-filter: blur(24px)` + transparência
- **Orbs animados:** 3 esferas com blur e animação float
- **Hover:** elevação com `translateY(-3px)` + box-shadow
- **Spinner:** loading no botão durante request
- **Anel SVG:** probabilidade animada com `strokeDashoffset`
- **Contador animado:** 0% → X% com easing cubic

### Responsividade

| Breakpoint | Layout                                    |
|------------|-------------------------------------------|
| `≥ 900px`  | Grid 2 colunas (form + resultado)         |
| `≤ 600px`  | Coluna única, header vertical             |
| `≤ 400px`  | Stats em coluna única                     |

## 4. Integração com API

| Função JS           | Endpoint   | Método | Ação                          |
|---------------------|------------|--------|-------------------------------|
| `submitPrediction()`| `/predict` | POST   | Envia dados para predição     |
| `fetchDrift()`      | `/drift`   | GET    | Busca estatísticas de drift   |

### Fluxo de Predição

1. Usuário preenche formulário (9 campos)
2. `validateForm()` valida campos (tipo, range, obrigatoriedade)
3. `submitPrediction()` envia POST com payload JSON
4. `displayResult()` renderiza resultado (badge + anel + detalhes)
5. `showToast()` exibe notificação de sucesso/erro

### Componentes

- **Formulário:** 3 seções (Dados Pessoais, Indicadores PEDE, Notas)
- **Card de Resultado:** status badge, anel de probabilidade SVG, detalhes
- **Stats Row:** 4 cards com métricas resumidas de drift
- **Tabela de Features:** estatísticas por feature com mini barras visuais
- **Toast:** notificação flutuante no rodapé

---

*Anterior: [06 - Observabilidade](./06-OBSERVABILIDADE.md) | Próximo: [08 - Deploy](./08-DEPLOY.md)*
