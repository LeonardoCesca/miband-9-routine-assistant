# band-routine-assistant

`band-routine-assistant` e um backend em Python para rotinas e micro-habitos com disparo automatizado via Telegram, registro de resposta do usuario e analise de adesao. A proposta do projeto e simples: enviar lembretes acionaveis para o iPhone, permitir resposta com um toque e armazenar historico e metricas no Supabase.

Na pratica, o fluxo funciona assim:
- um scheduler externo chama a API
- a API identifica lembretes elegiveis
- o Telegram entrega a notificacao
- o usuario responde com `Feito`, `Nao feito` ou `Adiar 15min`
- tudo fica registrado para analytics e auditoria

## Proposta de valor

- Disparo de lembretes recorrentes com baixo atrito
- Resposta em um toque com botoes inline no Telegram
- Persistencia de eventos para acompanhamento de adesao
- Arquitetura simples, separada por `agents`, `tools` e `services`
- Pronto para deploy com FastAPI + Supabase + Render

## Stack

- Python 3.11+
- FastAPI
- Uvicorn
- Supabase Python Client
- httpx
- python-dotenv
- pydantic-settings
- pytest
- pytest-asyncio
- Timezone `America/Sao_Paulo`
- Scheduler externo por HTTP

## Arquitetura

O projeto separa claramente responsabilidade de negocio e execucao tecnica:

- `Agent`: decide, coordena e orquestra fluxo
- `Tool`: executa uma acao tecnica reutilizavel
- `Service`: encapsula integracoes externas

### Agents

- `OrchestratorAgent`: coordena o ciclo de processamento de lembretes
- `SchedulerAgent`: executa a janela de processamento quando acionado externamente
- `ReminderAgent`: identifica lembretes elegiveis por horario e dia da semana
- `NotificationAgent`: envia mensagens prontas para o Telegram
- `LoggingAgent`: registra eventos como `sent`, `done`, `not_done`, `postponed` e `error`
- `AnalyticsAgent`: consolida metricas de adesao

### Tools

- `TelegramTool`: envio de mensagem e resposta a callback do Telegram
- `SupabaseTool`: operacoes de leitura, insercao, update e logs
- `TimeTool`: timezone, janela de processamento e regras de calendario
- `MessageTool`: montagem de texto e botoes inline

## Estrutura

```text
app/
  main.py
  config.py
  database.py
  models.py
  routes/
    users.py
    reminders.py
    telegram.py
    analytics.py
    scheduler.py
  agents/
  tools/
  services/
  sql/schema.sql
tests/
.github/workflows/scheduler.yml
.env.example
.gitignore
requirements.txt
render.yaml
README.md
```

## Modelo funcional

### Usuario

Cada usuario representa um destino de notificacao no Telegram:
- `name`
- `telegram_chat_id`

### Reminder

Cada reminder representa uma acao recorrente:
- `title`
- `message`
- `hour`
- `minute`
- `days_of_week`
- `active`

### Reminder logs

Cada interacao relevante gera rastreabilidade:
- `sent`
- `done`
- `not_done`
- `postponed`
- `error`

## API

### Endpoints principais

- `GET /health`
- `POST /users`
- `GET /users`
- `POST /reminders`
- `GET /reminders`
- `PATCH /reminders/{id}/toggle`
- `POST /telegram/webhook`
- `GET /analytics`
- `POST /scheduler/run`

### Exemplo de reminder

```json
{
  "user_id": "UUID_DO_USER",
  "title": "Segunda - Peitoral",
  "message": "Faca 1 serie agora.",
  "hour": 9,
  "minute": 0,
  "days_of_week": [0],
  "active": true
}
```

Padrao de `days_of_week`:
- `0` = segunda
- `1` = terca
- `2` = quarta
- `3` = quinta
- `4` = sexta
- `5` = sabado
- `6` = domingo

Se `days_of_week` nao for informado, o reminder vale para todos os dias.

## Variaveis de ambiente

Copie `.env.example` para `.env`:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
TELEGRAM_BOT_TOKEN=
APP_BASE_URL=
APP_TIMEZONE=America/Sao_Paulo
SCHEDULER_TOKEN=
```

## Banco no Supabase

1. Crie um projeto no Supabase.
2. Abra o `SQL Editor`.
3. Rode o SQL de [app/sql/schema.sql](/c:/Users/leona/Documents/band-routine-assistant/app/sql/schema.sql:1).
4. Em `Project Settings > API`, copie:
- `Project URL` para `SUPABASE_URL`
- `service_role` para `SUPABASE_SERVICE_ROLE_KEY`

Se o banco ja existir, rode tambem:

```sql
alter table reminders
add column if not exists days_of_week int[] not null default array[0,1,2,3,4,5,6];
```

## Setup local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Ambiente local:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Configuracao do Telegram

1. Crie um bot com `@BotFather`
2. Copie o token para `TELEGRAM_BOT_TOKEN`
3. Envie uma mensagem para o bot
4. Descubra o `telegram_chat_id`
5. Cadastre o usuario na API

### Webhook do Telegram

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=<APP_BASE_URL>/telegram/webhook
```

Conferencia:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo
```

## Scheduler externo recomendado

O projeto nao depende de APScheduler rodando dentro da web app. O processamento e acionado por um scheduler HTTP externo.

### Recomendacao

Para este projeto, a opcao mais simples e confiavel no plano free e usar `cron-job.org`.

Configuracao recomendada:
- URL: `https://miband-9-routine-assistant.onrender.com/scheduler/run`
- Method: `POST`
- Header: `X-Scheduler-Token: <SCHEDULER_TOKEN>`
- Frequencia: a cada 5 minutos

### Endpoint de scheduler

- `POST /scheduler/run`

Header obrigatorio:

```text
X-Scheduler-Token: <SCHEDULER_TOKEN>
```

### Regras de processamento

- processa uma janela atual de 5 minutos
- respeita dia da semana
- evita duplicidade usando `reminder_logs` com status `sent`

### Resposta do endpoint

Exemplo:

```json
{
  "processed": 1,
  "sent_keys": ["reminder-id:202606051000"],
  "current_time": "2026-06-05T10:03:12-03:00",
  "window_minutes": 5
}
```

Exemplo manual:

```bash
curl -X POST "$APP_BASE_URL/scheduler/run" \
  -H "X-Scheduler-Token: $SCHEDULER_TOKEN"
```

## Como configurar no cron-job.org

1. Crie uma conta em `cron-job.org`
2. Clique em `Create cronjob`
3. Configure:
- URL: `https://miband-9-routine-assistant.onrender.com/scheduler/run`
- Method: `POST`
- Schedule: `every 5 minutes`
4. Em headers, adicione:
- `X-Scheduler-Token: SEU_SCHEDULER_TOKEN`
5. Salve o job
6. Rode um teste manual

Vantagens:
- gratis
- simples
- nao depende do scheduler do GitHub Actions
- continua compativel com a arquitetura atual
- nao exige mudar o backend

## GitHub Actions

O workflow em [.github/workflows/scheduler.yml](/c:/Users/leona/Documents/band-routine-assistant/.github/workflows/scheduler.yml:1) pode ser mantido como opcao secundaria ou ferramenta de teste manual.

Ele e util para:
- `workflow_dispatch`
- testes operacionais
- comparacao entre scheduler externo e GitHub

## Deploy no Render

O arquivo [render.yaml](/c:/Users/leona/Documents/band-routine-assistant/render.yaml:1) ja define:

- build command: `pip install -r requirements.txt`
- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- health check: `/health`

Configure no Render:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `TELEGRAM_BOT_TOKEN`
- `APP_BASE_URL`
- `APP_TIMEZONE`
- `SCHEDULER_TOKEN`

Depois do deploy:
- teste `GET /health`
- acesse `GET /docs`
- valide manualmente `POST /scheduler/run`

## Exemplos de uso

### Criar usuario

```bash
curl -X POST "$APP_BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Leona\",\"telegram_chat_id\":\"SEU_CHAT_ID\"}"
```

### Criar reminder

```bash
curl -X POST "$APP_BASE_URL/reminders" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"UUID_DO_USER\",\"title\":\"Alongar\",\"message\":\"Hora da rotina\",\"hour\":9,\"minute\":30,\"days_of_week\":[0,1,2,3,4],\"active\":true}"
```

### Rodar scheduler manualmente

```bash
curl -X POST "$APP_BASE_URL/scheduler/run" \
  -H "X-Scheduler-Token: $SCHEDULER_TOKEN"
```

## Qualidade e testes

```powershell
pytest
```

A suite cobre:
- health check
- usuarios
- reminders
- toggle de ativacao
- callbacks do Telegram
- analytics
- deduplicacao do scheduler
- filtro por dia da semana
- arquivos de ambiente e seguranca basica

## Seguranca

- nao hardcode tokens ou chaves
- mantenha `.env` fora do versionamento
- use `SUPABASE_SERVICE_ROLE_KEY` apenas no backend
- proteja `/scheduler/run` com `SCHEDULER_TOKEN`
- nao exponha segredos em prints, logs ou clientes frontend

## Limitacoes atuais

- a vibracao da Mi Band depende do espelhamento de notificacoes do iPhone
- o projeto nao fala diretamente com a pulseira
- o Render free pode ter cold start
- o scheduler ideal para operacao free aqui e externo via HTTP

## Roadmap sugerido

- painel admin para calendarios e usuarios
- templates de rotina por programa
- retries e observabilidade de scheduler
- metricas por periodo e por tipo de rotina
- multi-tenant para uso comercial

## Licenca

Defina a licenca conforme a estrategia comercial do produto.
