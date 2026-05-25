# 🎬 CineBot — Agente de IAGen para Cinema

Projeto de IAGen: agente ReAct com base de dados de filmes e interface web com chat.

## Metodologia aplicada

- **Agente de IA** com loop ReAct (Razão → Ação → Observação)
- **LLM como motor de raciocínio** (Claude Sonnet)
- **Tools via MCP-style** (get_schema, query_movies_db)
- **Memória short-term** (histórico de conversa por sessão)
- **Base de dados** SQLite com 50 filmes clássicos e modernos

## Stack

- Python + Flask (backend)
- Anthropic API (LLM + agente)
- SQLite (base de dados)
- HTML/CSS/JS (frontend — site com chat)

## Como rodar

### 1. Instalar dependências

```bash
pip install flask anthropic pandas
```

### 2. Configurar API key

```bash
export ANTHROPIC_API_KEY="sua_chave_aqui"
```

### 3. Iniciar o servidor

```bash
python app.py
```

### 4. Acessar

Abra o navegador em: http://localhost:5000

## Estrutura

```
iagen-filmes/
├── app.py          # Backend Flask + Agente ReAct
├── movies.db       # SQLite com 50 filmes
├── movies.csv      # Dataset de filmes
└── static/
    └── index.html  # Frontend (site com chat)
```

## Exemplos de perguntas

- "Qual o filme mais bem avaliado da base?"
- "Me recomende um sci-fi clássico"
- "Quais filmes do Christopher Nolan estão na base?"
- "Filmes em português acima de 8.0 de rating"
- "Qual o filme com mais votos?"
- "Dramas lançados depois de 2010"

## Arquitetura do Agente

```
Usuário → Pergunta
         ↓
    LLM Raciocina
         ↓
    Usa Tool (SQL)
         ↓
    Observa Resultado
         ↓
    Sintetiza Resposta
         ↓
Usuário ← Resposta em PT-BR
```
