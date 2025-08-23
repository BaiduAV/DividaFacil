# DividaFácil Web

Pequena aplicação FastAPI + Jinja para divisão de despesas.

## Visão geral

- Backend: FastAPI + Uvicorn
- Templates: Jinja2 + Tailwind utility classes
- Banco: SQLite (dev) ou PostgreSQL (produção) via `DATABASE_URL`
- Container: Dockerfile pronto

## Executando localmente

Pré-requisitos: Python 3.13, pip, virtualenv.

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn web_app:app --reload
```

Acesse http://localhost:8000

### Variáveis de ambiente (local)

Você pode copiar `.env.example` para `.env` e ajustar valores:

- `APP_NAME` (default: DividaFacil)
- `DEBUG` (default: false)
- `LOG_LEVEL` (default: INFO)
- `TEMPLATES_DIR` (default: templates)
- `STATIC_DIR` (default: static)
- `DATABASE_URL`
  - Ex.: `sqlite:///./dividafacil.db` (padrão dev)
  - Ex.: `postgres://USER:PASS@HOST:PORT/DBNAME` (produção; o app normaliza para `postgresql+psycopg2`)

## Testes

```bash
pytest -q
```

## Docker

```bash
docker build -t splitwise-web .
docker run -p 8000:8000 --env LOG_LEVEL=INFO splitwise-web
```

## Configuração

Variáveis de ambiente suportadas (veja `src/settings.py`):

- `APP_NAME` (default: DividaFácil)
- `DEBUG` (default: false)
- `LOG_LEVEL` (default: INFO)
- `TEMPLATES_DIR` (default: templates)
- `STATIC_DIR` (default: static)
- `DATABASE_URL` (SQLite dev por padrão; PostgreSQL em produção)

## Estrutura

- `web_app.py`: app FastAPI, rotas e templates
- `src/models/`: entidades de domínio
- `src/services/`: regras de negócio
- `src/settings.py`: configuração centralizada
- `src/logging_config.py`: setup de logging
- `src/filters.py`: filtros Jinja
- `templates/`: HTML
- `static/`: assets estáticos
- `tests/`: suite de testes

## Segurança e produção

- Ativar proxies/servidor de aplicação (Gunicorn/Uvicorn workers) quando necessário
- Adicionar cabeçalhos de segurança (CSP, HSTS) e TLS no reverso (Nginx ou provedor)
- Implementar autenticação/autorização (não implementado)
- Usar banco de dados real via repositórios (a implementar)

---

## Deploy para produção (GitHub + Render)

O repositório já contém um `Dockerfile`. No Render, basta criar um serviço web usando o repositório GitHub.

### Opção A) Blueprint (IaC com `render.yaml`)

Automatiza a criação do Web Service e do PostgreSQL via código.

1. Suba o projeto ao GitHub
2. No Render: New → Blueprint → selecione o repositório
3. Confirme o plano/região (defaults no `render.yaml`: `free`/`oregon`)
4. Deploy

Detalhes do `render.yaml`:
- Serviço web `dividafacil-web` (Docker) com health check em `/healthz`
- Banco `dividafacil-db` (PostgreSQL)
- `DATABASE_URL` do serviço web é mapeado do DB com `internalConnectionString`

### 1) Subir para o GitHub

```bash
git init
git add .
git commit -m "Initial production-ready setup"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/<seu-repo>.git
git push -u origin main
```

### Opção B) Criar serviço no Render (via Docker) manualmente

1. Acesse o Render e crie um novo Web Service
2. Conecte ao repositório GitHub
3. Render detectará o `Dockerfile` automaticamente
4. Configure:
   - Runtime: Docker
   - Região: a mais próxima
   - Plano: gratuito (para testes)
   - Variáveis de ambiente:
     - `DATABASE_URL` = string do PostgreSQL do Render (ex.: `postgres://...`)
     - `LOG_LEVEL` = `INFO`
     - `APP_NAME` = `DividaFacil` (opcional)
5. Clique em Deploy

O container expõe a porta 8000 (`EXPOSE 8000`) e inicia com:

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

### 3) Banco de dados (PostgreSQL no Render)

1. Crie um serviço PostgreSQL no Render
2. Copie o `External Connection String`
3. No serviço web, defina `DATABASE_URL` com essa URL (formato `postgres://...`)
   - O app faz a normalização para `postgresql+psycopg2`

### 4) Variáveis importantes

- `DATABASE_URL`: obrigatório em produção
- Outras (opcionais): `APP_NAME`, `LOG_LEVEL`, `DEBUG=false`

### 5) Observações

- Migrações de banco: não há Alembic configurado; a app cria as tabelas básicas automaticamente. Se for migrar dados do SQLite, faça export/import manualmente ou adicione Alembic.
- Logs: `LOG_LEVEL=INFO` recomendado.
- Escalonamento: se precisar de workers, ajuste o comando para Gunicorn+Uvicorn, ou use autoscale do Render.

## Troubleshooting

- Erro de conexão com banco em produção: verifique `DATABASE_URL` e se o serviço PostgreSQL está acessível.
- Porta incorreta: mantenha `--port 8000` no container; o Render faz o mapeamento externo.
- Estáticos/templates: os defaults (`templates/`, `static/`) já estão incluídos na imagem.
 - Health check: o endpoint `GET /healthz` retorna `{ "status": "ok" }`. Configure-o no Render como health check se desejar.
