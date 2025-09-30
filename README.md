<div align="center">

# DividaFácil

Aplicação completa para dividir despesas entre pessoas e grupos. Suporte a divisão igual, valores exatos e porcentagens, parcelas, cálculo de saldos e notificações – com frontend moderno (React + Vite) e backend robusto (FastAPI).

</div>

---

## ✨ Principais Recursos

Backend / Domínio:
- Autenticação baseada em sessão (cookies)  
- Usuários, grupos e associação de membros  
- Despesas com divisão: igual / exata / porcentagem  
- Parcelamento (instalments) e acompanhamento de vencimentos  
- Cálculo de saldos e orientação para acertos  
- Scripts de notificação (atrasadas e próximas)  
- Internacionalização (pt-BR e en – expansível)  

Frontend:
- React + Vite + TypeScript  
- Componentização moderna e acessível  
- Gerenciamento de estado via Context API  
- Camada de API e tratamento de erros centralizado  
- Build de produção servido pelo FastAPI em `/app`  

Qualidade & Ferramentas:
- CLI interativa (`backend/main.py`)  
- Testes automatizados (pytest)  
- Logging estruturado  
- Migrações (Alembic inicializado)  

---

## 🏗 Arquitetura

```
DividaFacil/
├── backend/                  # Backend FastAPI
│   ├── src/                  # Código Python (models, services, routers, etc.)
│   ├── tests/                # Testes (pytest)
│   ├── alembic/              # Migrações de banco
│   ├── static/               # Arquivos estáticos (quando usados)
│   ├── locales/              # Arquivos de i18n
│   ├── web_app.py            # App ASGI principal
│   ├── main.py               # CLI interativa
│   ├── requirements.txt      # Dependências Python
│   └── pyproject.toml        # Configuração de ferramentas
├── frontend/                 # Frontend React + Vite
│   ├── src/                  # Código TypeScript
│   ├── build/                # Saída de produção (gerada)
│   ├── index.html            # Entrada Vite
│   └── package.json          # Dependências Node
├── start-app.ps1             # Script unificado (Windows)
├── start-app.sh              # Script unificado (Linux/macOS)
└── README.md
```

Responsabilidades em execução:
- API REST: `/api/*`  
- Health check: `/healthz`  
- SPA React: `/app` (raiz `/` redireciona)  
- Assets estáticos: `/static/*`  

---

## 🚀 Início Rápido

### 1. Requisitos
| Componente | Versão | Observação |
|------------|--------|------------|
| Python | 3.12+ | Use ambiente virtual |
| Node.js | 18+ | Inclui npm |
| Git | recente | Clonar repositório |

### 2. Um Comando (Recomendado)

```powershell
# Windows
./start-app.ps1
```
```bash
# Linux/macOS
./start-app.sh
```

O script instala dependências, cria venv (se necessário), constrói o frontend e inicia backend + frontend.

### 3. Manual (Backend)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn web_app:app --reload --port 8000
```

### 4. Manual (Frontend)
```bash
cd frontend
npm install
npm run dev      # Desenvolvimento: http://localhost:3000
npm run build    # Produção: gera pasta build/
```

O backend serve o build (se existente) em `/app`.

### 5. Endpoints Principais
| Propósito | URL |
|-----------|-----|
| Aplicação Web | http://localhost:8000/ (→ /app) |
| SPA React | http://localhost:8000/app |
| API Root | http://localhost:8000/api |
| Health Check | http://localhost:8000/healthz |
| Documentação OpenAPI | http://localhost:8000/docs |

---

## � Scripts Unificados

Windows (PowerShell):
```powershell
./start-app.ps1                 # Inicia tudo
./start-app.ps1 -Mode backend   # Só backend
./start-app.ps1 -Mode frontend  # Só frontend
./start-app.ps1 -Port 8080 -FrontendPort 3100
./start-app.ps1 -NoBuild        # Não reconstruir frontend
```

Linux / macOS:
```bash
./start-app.sh                  # Inicia tudo
./start-app.sh -m backend       # Só backend
./start-app.sh -m frontend      # Só frontend
./start-app.sh -p 8080 -f 3100  # Portas customizadas
./start-app.sh -n               # Pular build
```

---

## 🧪 Testes
```bash
cd backend
python -m pytest -q
```
Alguns testes que fazem requisições reais exigem o backend rodando em `:8000`.

Dados de exemplo & notificações:
```bash
cd backend
python create_test_data.py
python scripts/notifications.py overdue --report-only
python scripts/notifications.py upcoming --report-only
```

Frontend (se configurado):
```bash
cd frontend
npm test
```

---

## 💻 CLI Interativa
```bash
cd backend
python main.py
```
Funções: criar grupos, adicionar despesas, ver saldos, sugerir acertos.

---

## ⚙️ Variáveis de Ambiente
| Variável | Default | Uso |
|----------|---------|-----|
| APP_NAME | DividaFácil | Nome da aplicação |
| DEBUG | false | Modo debug |
| LOG_LEVEL | INFO | Nível de log |
| DATABASE_URL | sqlite:///./dividafacil.db | Banco (usar PostgreSQL em produção) |
| SESSION_SECRET_KEY | (dev) | Assinatura de sessão |
| STATIC_DIR | static | Diretório estático |
| LOCALES_DIR | locales | Diretório de i18n |
| DEFAULT_LOCALE | pt-BR | Locale padrão |

SMTP opcional:
| Variável | Exemplo |
|----------|---------|
| SMTP_SERVER | smtp.gmail.com |
| SMTP_PORT | 587 |
| SMTP_USERNAME | seu-email@gmail.com |
| SMTP_PASSWORD | senha-ou-app-password |

Você pode usar `.env` localmente (não commitar credenciais sensíveis).

---

## 🗄 Banco de Dados & Migrações
Desenvolvimento usa SQLite automaticamente. Para evoluir schema:
```bash
cd backend
alembic revision --autogenerate -m "descricao"
alembic upgrade head
```
Reset rápido (dev):
```bash
rm dividafacil.db   # Windows: Remove-Item dividafacil.db
python -c "from src.database import create_tables; create_tables()"
```
Produção: defina `DATABASE_URL=postgresql+psycopg2://usuario:senha@host/db`.

---

## 🔐 Segurança
- Alterar `SESSION_SECRET_KEY` em produção  
- Usar HTTPS (fornecido pela plataforma)  
- Reforçar CSP e cabeçalhos se necessário  
- Rotacionar credenciais periodicamente  

---

## 🔌 Principais Endpoints API (`/api`)
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET  /api/users`
- `POST /api/groups`
- `GET  /api/groups/{group_id}/expenses`
- `POST /api/expenses`

Explorar docs interativos: `/docs`.

---

## 🌍 Internacionalização
- Arquivos em `backend/locales/`  
- Padrão: `pt-BR`  
- Adicione novos JSON para mais idiomas  

---

## 🧹 Qualidade de Código
```bash
cd backend
pip install black ruff isort
black .
isort .
ruff check .
```

---

## 🛠 Solução de Problemas
| Problema | Causa provável | Ação |
|----------|----------------|------|
| Erros de import | venv não ativada | Ative e reinstale deps |
| Página em branco | Sem build | `npm run build` em `frontend/` |
| 404 SPA | Caminho errado | Use `/app` |
| Banco travado (SQLite) | Interrupção abrupta | Remover arquivo e recriar |
| Testes HTTP falhando | Backend parado | Subir servidor antes |
| Email não enviado | SMTP ausente | Definir variáveis SMTP_* |

Health check:
```bash
curl http://localhost:8000/healthz
```

---

## 🚀 Deploy (Exemplo Render)
Passos gerais:
1. Build do frontend (`npm run build`)
2. Instalar dependências Python
3. Rodar: `python -m uvicorn web_app:app --host 0.0.0.0 --port 8000`

Variáveis típicas:
```
APP_NAME=DividaFácil
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg2://user:senha@host/db
SESSION_SECRET_KEY=trocar-em-producao
```

---

## 🧭 Ideias Futuras
- Sugestões de acerto mais inteligentes  
- Templates de e‑mail ricos  
- Suporte multi‑moeda  
- Exportação CSV / PDF  
- Atualização em tempo real (WebSocket)  

---

## 🤝 Contribuindo
```bash
git clone <url-repo>
cd DividaFacil
./start-app.ps1   # ou ./start-app.sh
git checkout -b feature/minha-melhora
python -m pytest -q
git commit -am "feat: minha melhoria"
git push origin feature/minha-melhora
# Abra o PR
```
Mantenha commits objetivos e execute os testes antes de enviar.

---

## 📄 Licença
MIT (adicione arquivo LICENSE se ainda não existir).

---

## 🙌 Agradecimentos
- FastAPI, Pydantic, SQLAlchemy  
- Comunidade React / Vite  
- Ecosistema open-source  

---

Boas divisões! 💸


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

### Proteção CSRF
O backend implementa proteção CSRF para métodos de modificação (`POST`, `PUT`, `DELETE`, etc.) em rotas sob `/api/*` usando estratégia de **double-submit token** armazenado em sessão.

Fluxo:
1. Autenticar (signup/login) – estes endpoints são isentos de CSRF para permitir bootstrap da sessão.
2. Obter token: `GET /api/csrf-token` → `{ "csrf_token": "...", "header": "X-CSRF-Token" }`
3. Incluir o header `X-CSRF-Token` com o valor retornado em cada requisição de escrita.

Se token faltar ou for inválido: resposta `403 {"detail": "Missing or invalid CSRF token"}`.

No frontend: buscar o token após login e armazenar em memória (ou contexto); renovar se a sessão for reiniciada.

### Audit Log
Eventos de segurança e operações sensíveis são registrados em arquivo JSON-lines (padrão: `audit.log`). Cada linha contém:
```json
{"ts":"2025-09-30T12:34:56.123456+00:00","event":"group.created","actor_id":"<uuid>","actor_ip":"127.0.0.1","details":{"group_id":"...","name":"..."}}
```
Eventos atuais:
- `group.created`, `group.deleted`
- `expense.created`, `expense.deleted`

Configuração:
- Caminho via env `AUDIT_LOG_FILE` (default `audit.log`).
- Rotação deve ser feita externamente (logrotate / stdout collector).

### Cookies de Sessão
Flags de endurecimento:
- `https_only` (Secure) habilitado quando `SESSION_COOKIE_SECURE=true`.
- SameSite padrão (implementação atual do framework) visa comportamento Lax; variável `SESSION_COOKIE_SAMESITE` disponível para evolução futura.

Recomendações produção:
```
SESSION_COOKIE_SECURE=true
SESSION_SECRET_KEY=<valor forte>
```

- `src/settings.py`: configuração centralizada
- `src/logging_config.py`: setup de logging
- `src/filters.py`: filtros Jinja
- `templates/`: HTML
- `static/`: assets estáticos
 Os testes agora usam **FastAPI TestClient in‑process**, não sendo necessário subir servidor separado. Testes de integração externos foram adaptados / marcados como opcionais. Para habilitar teste de conectividade do frontend dev server exporte `RUN_REACT_E2E=1`.

### Testes de CSRF
`tests/test_csrf.py` valida cenários: ausência, token inválido e token válido.

### Teste de Métricas
`tests/test_metrics.py` garante presença de novos contadores.

### Teste de Audit Log
`tests/test_audit.py` valida que criação de grupo e despesa geram entradas estruturadas.


### CSRF
- `GET /api/csrf-token` – retorna token para headers de escrita.

### Métricas & Health
- `GET /metrics` – Exposição Prometheus (texto) com contadores básicos e status.
- `GET /healthz` – Liveness check.
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

### Scrape de Métricas (Prometheus / Render / etc.)
Basta configurar serviço para coletar `GET /metrics`. Exemplo Prometheus:
```yaml
scrape_configs:
   - job_name: 'dividafacil'
      metrics_path: /metrics
      static_configs:
         - targets: ['app:8000']
```

### Cabeçalhos Importantes
Os cabeçalhos de segurança (CSP, X-Frame-Options, etc.) já vêm configurados; ajuste conforme necessidades de CDN ou fontes externas.
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
