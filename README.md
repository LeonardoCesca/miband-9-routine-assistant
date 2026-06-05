# band-routine-assistant

Backend em Python com FastAPI para enviar lembretes via Telegram. Quando a notificacao chega no iPhone, a Xiaomi Smart Band 9 Pro pode vibrar ao espelhar a notificacao do Telegram. Os botoes inline permitem registrar `done`, `not_done` e `postponed`, e tudo fica salvo no Supabase.

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
- GitHub Actions como scheduler externo

## Arquitetura

`Agent` decide ou coordena uma responsabilidade.

`Tool` executa uma acao tecnica reutilizavel.

- `OrchestratorAgent`: coordena disparo e logging dos lembretes.
- `SchedulerAgent`: processa uma janela de 5 minutos quando o endpoint externo e chamado.
- `ReminderAgent`: busca lembretes ativos, filtra os da janela atual e monta o payload.
- `NotificationAgent`: envia mensagem pronta via Telegram.
- `LoggingAgent`: persiste eventos `sent`, `done`, `not_done`, `postponed` e `error`.
- `AnalyticsAgent`: consolida metricas de uso.

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

## Variaveis de ambiente

Copie `.env.example` para `.env` e preencha:

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

## Setup local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API local:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Telegram

1. Crie um bot com `@BotFather`.
2. Copie o token para `TELEGRAM_BOT_TOKEN`.
3. Envie uma mensagem para o bot.
4. Descubra o `telegram_chat_id`.
5. Crie um usuario via `POST /users`.

Webhook:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=<APP_BASE_URL>/telegram/webhook
```

Conferencia:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getWebhookInfo
```

## Scheduler externo

O projeto nao usa mais APScheduler rodando dentro do Render. O scheduler agora fica no GitHub Actions e chama a API em hora cheia.

Endpoint:

- `POST /scheduler/run`

Protecao:

- Header obrigatorio `X-Scheduler-Token`
- Valor lido de `SCHEDULER_TOKEN`

Exemplo:

```bash
curl -X POST "$APP_BASE_URL/scheduler/run" \
  -H "X-Scheduler-Token: $SCHEDULER_TOKEN"
```

Regra de envio:

- o backend processa a janela atual de 5 minutos
- se ja existir log `sent` para o mesmo reminder dentro da mesma janela, ele nao reenviara

## GitHub Actions

O workflow ja esta pronto em [.github/workflows/scheduler.yml](/c:/Users/leona/Documents/band-routine-assistant/.github/workflows/scheduler.yml:1).

Ele roda:

- a cada hora cheia
- manualmente por `workflow_dispatch`

Configure estes `Repository Secrets` no GitHub:

- `APP_BASE_URL`
- `SCHEDULER_TOKEN`

O workflow faz:

```bash
curl -X POST "$APP_BASE_URL/scheduler/run" \
  -H "X-Scheduler-Token: $SCHEDULER_TOKEN"
```

## Deploy gratis no Render

O arquivo [render.yaml](/c:/Users/leona/Documents/band-routine-assistant/render.yaml:1) ja define:

- build command: `pip install -r requirements.txt`
- start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- health check: `/health`

No Render, configure:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `TELEGRAM_BOT_TOKEN`
- `APP_BASE_URL`
- `APP_TIMEZONE`
- `SCHEDULER_TOKEN`

Depois do deploy, teste:

- `<APP_BASE_URL>/health`
- `<APP_BASE_URL>/docs`

## Endpoints

- `GET /health`
- `POST /users`
- `GET /users`
- `POST /reminders`
- `GET /reminders`
- `PATCH /reminders/{id}/toggle`
- `POST /telegram/webhook`
- `GET /analytics`
- `POST /scheduler/run`

## Exemplos de uso

Criar usuario:

```bash
curl -X POST "$APP_BASE_URL/users" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Leona\",\"telegram_chat_id\":\"SEU_CHAT_ID\"}"
```

Criar reminder:

```bash
curl -X POST "$APP_BASE_URL/reminders" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"UUID_DO_USER\",\"title\":\"Alongar\",\"message\":\"Hora da rotina\",\"hour\":9,\"minute\":30,\"active\":true}"
```

Rodar scheduler manualmente:

```bash
curl -X POST "$APP_BASE_URL/scheduler/run" \
  -H "X-Scheduler-Token: $SCHEDULER_TOKEN"
```

## Testes

```powershell
pytest
```

## Observacoes

- O webhook processa `callback_query`, sem polling.
- A acao `postponed` registra no `metadata` o horario atual e o horario sugerido de `+15min`.
- Nesta fase o adiamento e registrado como evento analitico e nao altera o horario persistido do reminder.
