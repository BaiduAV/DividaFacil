# DividaFácil Web

Aplicação moderna para divisão de despesas com interface React e backend FastAPI.

## Visão geral

- **Frontend**: React + Vite + Tailwind CSS + Radix UI
- **Backend**: FastAPI + Uvicorn (API-only)
- **Banco**: SQLite (desenvolvimento) ou PostgreSQL (produção) via `DATABASE_URL`
- **Deploy**: Render (Python runtime)

## Arquitetura

A aplicação segue uma arquitetura moderna com separação clara entre frontend e backend:

- **Frontend React**: Single Page Application (SPA) servida pelo backend FastAPI
- **Backend FastAPI**: API REST pura para operações de dados (sem templates)
- **Banco de dados**: SQLAlchemy com suporte a SQLite/PostgreSQL
- **Autenticação**: Sistema de sessões com middleware FastAPI
- **Comunicação**: Frontend se conecta à API via HTTP requests

## Como funciona

1. **Backend FastAPI** serve a API REST em `/api/*` e a aplicação React em todas as outras rotas
2. **Frontend React** é construído para produção e seus assets são servidos estaticamente
3. **Autenticação** usa sessões HTTP mantidas via cookies
4. **Estado da aplicação** é gerenciado no frontend React com Context API
5. **API calls** são feitos via cliente HTTP customizado com interceptação de erros

## Executando localmente

### Pré-requisitos

- Python 3.12+ (recomendado 3.13)
- Node.js 18+ e npm
- Git

### 1. Clonagem e setup do backend

```bash
git clone <seu-repositorio>
cd DividaFacil

# Criar ambiente virtual
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Instalar dependências Python
pip install -r requirements.txt
```

### 2. Setup do frontend

```bash
# Instalar dependências Node.js
cd frontend
npm install

# Construir aplicação React para produção
npm run build

# Voltar para raiz do projeto
cd ..
```

### 3. Executar a aplicação

```bash
# Executar servidor FastAPI (serve API e frontend React)
uvicorn web_app:app --reload --host 127.0.0.1 --port 8000
```

Acesse: http://localhost:8000

### Endpoints principais

- **Aplicação React**: `http://localhost:8000/` (SPA principal)
- **API Health Check**: `http://localhost:8000/api/healthz`
- **API Endpoints**: `http://localhost:8000/api/*`

## Desenvolvimento

### Desenvolvimento com hot-reload

Para desenvolvimento com recarregamento automático:

```bash
# Terminal 1: Backend FastAPI
uvicorn web_app:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Frontend React (desenvolvimento)
cd frontend
npm run dev
```

O frontend de desenvolvimento roda em `http://localhost:3000` e faz proxy para a API em `http://localhost:8000`.

### Executando testes

```bash
# Testes Python
pytest -q

# Criar dados de teste
python create_test_data.py

# Executar notificações (teste)
python scripts/notifications.py overdue --report-only
```

### Variáveis de ambiente

Você pode configurar variáveis de ambiente em um arquivo `.env`:

```bash
# Aplicação
APP_NAME=DividaFácil
DEBUG=true
LOG_LEVEL=INFO

# Banco de dados
DATABASE_URL=sqlite:///./dividafacil.db

# Sessão
SESSION_SECRET_KEY=your-secret-key-change-in-production

# Email (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Estrutura do projeto

```
DividaFacil/
├── frontend/                 # Aplicação React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── ui/          # Componentes UI (Radix UI)
│   │   │   └── ...
│   │   ├── services/        # API client e utilities
│   │   ├── contexts/        # React contexts (Auth, etc.)
│   │   ├── App.tsx          # Componente principal
│   │   └── main.tsx         # Ponto de entrada
│   ├── build/               # Build de produção (gerado)
│   ├── package.json
│   └── vite.config.ts       # Configuração Vite
├── src/                     # Código Python backend
│   ├── models/              # Modelos de dados
│   ├── services/            # Lógica de negócio
│   ├── routers/             # Rotas FastAPI
│   ├── repositories/        # Acesso a dados
│   ├── schemas/             # Schemas Pydantic
│   ├── auth.py              # Autenticação
│   ├── database.py          # Configuração banco
│   ├── settings.py          # Configurações
│   └── logging_config.py    # Setup de logging
├── scripts/                 # Scripts utilitários
├── tests/                   # Testes
├── web_app.py               # Aplicação FastAPI principal (API + SPA serving)
├── main.py                  # CLI interface
├── requirements.txt         # Dependências Python
└── README.md
```

## Funcionalidades

### Frontend React
- **Interface moderna**: Design responsivo com Tailwind CSS
- **Componentes UI**: Radix UI para acessibilidade
- **Navegação SPA**: Roteamento client-side
- **Formulários**: Validação com React Hook Form
- **Notificações**: Sistema de toast com Sonner

### Backend API
- **REST API**: Endpoints para usuários, grupos e despesas
- **API-only**: Sem templates ou renderização server-side
- **SPA serving**: Serve aplicação React como assets estáticos
- **Autenticação**: Sistema de sessões HTTP
- **Validação**: Pydantic models
- **Banco de dados**: SQLAlchemy ORM
- **Internacionalização**: Suporte a português brasileiro

### Recursos principais
- ✅ Gerenciamento de usuários
- ✅ Criação de grupos
- ✅ Divisão de despesas (igual, exata, porcentagem)
- ✅ Parcelamento de despesas
- ✅ Cálculo automático de saldos
- ✅ Sistema de notificações
- ✅ Interface web moderna
- ✅ CLI para operações avançadas

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

## Deploy para produção (GitHub + Render)

A aplicação está configurada para deploy usando **Python runtime** no Render, com build automático do frontend React.

### 1. Preparar o projeto

```bash
# Construir frontend para produção
cd frontend
npm install
npm run build
cd ..

# Commit das mudanças
git add .
git commit -m "Update production build"
git push origin main
```

### 2. Deploy no Render

#### Opção A) Usando render.yaml (Recomendado)

O `render.yaml` automatiza a criação dos serviços:

1. **Suba o projeto ao GitHub**
2. **No Render**: New → Blueprint → selecione o repositório
3. **Confirme** o plano/região (Python runtime, região Oregon)
4. **Deploy**

O `render.yaml` cria:
- **Web Service**: Aplicação Python com build automático
- **PostgreSQL**: Banco de dados para produção
- **Health check**: Endpoint `/healthz`

#### Opção B) Criação manual

1. **Crie um Web Service** no Render
2. **Conecte** ao repositório GitHub
3. **Configure**:
   - **Runtime**: Python 3
   - **Build Command**: `cd frontend && npm install && npm run build && cd ..`
   - **Start Command**: `uvicorn web_app:app --host 0.0.0.0 --port 10000`
   - **Região**: Oregon (ou a mais próxima)
   - **Plano**: Gratuito para testes

4. **Variáveis de ambiente**:
   ```
   DATABASE_URL=postgres://... (do banco PostgreSQL)
   LOG_LEVEL=INFO
   APP_NAME=DividaFácil
   SESSION_SECRET_KEY=your-production-secret
   ```

### 3. Banco de dados PostgreSQL

1. **Crie um PostgreSQL** no Render
2. **Copie** o `External Connection String`
3. **Configure** `DATABASE_URL` no web service

### 4. Build automático

O Render executa automaticamente:
```bash
# Build do frontend
cd frontend
npm install
npm run build

# Setup Python
pip install -r requirements.txt

# Start da aplicação
uvicorn web_app:app --host 0.0.0.0 --port 10000
```

### 5. Verificação do deploy

- **Health check**: `GET /healthz` retorna `{"status": "ok"}`
- **Frontend**: Acesse a URL do Render - deve carregar a interface React
- **API**: Endpoints disponíveis em `/api/*`

## Segurança e produção

- ✅ **Autenticação**: Sistema de sessões implementado
- ✅ **Banco PostgreSQL**: Produção com SQLAlchemy
- ✅ **Build seguro**: Frontend construído em produção
- ✅ **Health checks**: Monitoramento automático
- ⚠️  **HTTPS**: Configurado automaticamente pelo Render
- ⚠️  **Cabeçalhos de segurança**: Recomendado adicionar CSP no futuro
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

### Problemas comuns no desenvolvimento

**Frontend não carrega (blank page)**
```bash
# Reconstruir frontend
cd frontend
rm -rf build
npm install
npm run build
cd ..
# Reiniciar servidor
uvicorn web_app:app --reload
```

**Assets não carregam**
- Verifique se `frontend/build/` existe e contém `index.html` e `assets/`
- Confirme que `vite.config.ts` tem `base: '/app/'`
- Verifique logs do servidor para erros 404 em assets

**API não responde**
```bash
# Testar health check
curl http://localhost:8000/healthz
# Deve retornar: {"status": "ok"}
```

**Erro de banco de dados**
```bash
# Resetar banco SQLite (desenvolvimento)
rm dividafacil.db
python -c "from src.database import create_tables; create_tables()"
```

### Problemas no deploy Render

**Build falha**
- Verifique se `package.json` tem as dependências corretas
- Confirme que `vite.config.ts` está configurado para produção
- Verifique logs do build no Render

**Aplicação não inicia**
- Porta incorreta: Render usa porta 10000 por padrão
- `DATABASE_URL` não configurada para PostgreSQL
- `SESSION_SECRET_KEY` não definida

**Frontend não carrega em produção**
- Verifique se o build do frontend foi executado
- Confirme que `frontend/build/` foi criado
- Verifique se assets estão sendo servidos de `/app/assets/`

### Interface CLI

A aplicação também oferece uma interface de linha de comando para operações avançadas:

```bash
# Executar interface interativa
python main.py

# Sistema de notificações
python scripts/notifications.py overdue --report-only
python scripts/notifications.py upcoming --report-only

# Criar dados de teste
python create_test_data.py
```

### Desenvolvimento avançado

**Hot reload para desenvolvimento**
```bash
# Backend
uvicorn web_app:app --reload --host 127.0.0.1 --port 8000

# Frontend (terminal separado)
cd frontend
npm run dev  # Roda em http://localhost:3000
```

**Debugging**
```bash
# Logs detalhados
LOG_LEVEL=DEBUG uvicorn web_app:app --reload

# Testes com coverage
pytest --cov=src --cov-report=html
```

**Internacionalização**
- Arquivos de tradução: `locales/pt-BR.json`, `locales/en.json`
- Locale padrão: `pt-BR` (configurável via `DEFAULT_LOCALE`)
