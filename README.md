# GERDAU - Sistema de Tomada de Decisão Operacional (MVP)

Este repositório contém um MVP funcional simples que implementa:
- Upload de planilhas Excel (ETL básico)
- Consolidação em banco SQLite
- Dashboard simples com KPIs e Top 5 custos

Baseado no documento de entrega final da Residência Tecnológica (RiseUp 2025.2).

## Como executar (local com Docker)

Requisitos: Docker e Docker Compose.

1. Construa e suba os serviços:
```bash
docker-compose up --build
```

2. Acesse o frontend:
http://localhost:5173

3. A API estará em:
http://localhost:8000

- Endpoint de upload: `POST /upload-excel` (form-data `file`)
- Endpoint de KPIs: `GET /kpis`
- Endpoint para baixar o DB (debug): `GET /download-db`

## Estrutura do projeto

- `backend/app/main.py` — FastAPI que processa Excel e armazena em SQLite
- `frontend/index.html` — Interface simples para upload e visualização
- `docker-compose.yml` — configuração para backend + frontend
- `backend/requirements.txt` — dependências Python

## Formato esperado da planilha

A planilha deve conter colunas (nomes em português):
- `periodo` (ex: 2024-01)
- `centro_custo`
- `tipo_custo`
- `valor` (número)

## Próximos passos (evoluções sugeridas)
- Conector real com SAP (BAPI / JCo)
- Construtor de relatórios drag & drop
- Detecção de anomalias com ML
- Previsão de custos e busca por linguagem natural

## Observações
Este MVP foi criado como entrega inicial e pode ser expandido conforme o backlog do produto.
