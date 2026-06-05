# band-routine-assistant

`band-routine-assistant` e uma infraestrutura backend para lembretes recorrentes via Telegram, com confirmacao de execucao pelo usuario, persistencia de historico e base para analytics de adesao.

O produto foi desenhado para cenarios de rotina, bem-estar, accountability e micro-habitos, com foco em:
- baixo atrito para o usuario final
- operacao simples
- integracao barata e escalavel
- arquitetura clara para evolucao comercial

## O que o produto entrega

- Disparo automatizado de lembretes por agenda
- Resposta em um toque no Telegram
- Registro de `feito`, `nao feito` e `adiado`
- Persistencia de eventos e auditoria no Supabase
- Regras por horario e dia da semana
- Base pronta para metricas, painel e monetizacao futura

## Fluxo do produto

1. Um scheduler HTTP externo chama `POST /scheduler/run`
2. A API identifica reminders elegiveis
3. O Telegram entrega a notificacao ao usuario
4. O usuario responde via botoes inline
5. O backend registra tudo no Supabase

## Casos de uso

- Rotina de exercicios ao longo do dia
- Habit tracking
- Programas de treino por dia da semana
- Lembretes de autocuidado
- Protocolos de reabilitacao ou adesao
- MVPs wellness ou health accountability

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
- Scheduler HTTP externo

## Arquitetura

O projeto separa claramente regra de negocio, orquestracao e execucao tecnica.

- `Agent`: decide, coordena e orquestra o fluxo
- `Tool`: executa uma acao tecnica reutilizavel
- `Service`: encapsula integracoes externas

### Agents

- `OrchestratorAgent`: coordena o ciclo de processamento
- `SchedulerAgent`: executa a janela de reminders quando acionado externamente
- `ReminderAgent`: filtra reminders por horario e dia da semana
- `NotificationAgent`: envia mensagens para o Telegram
- `LoggingAgent`: registra eventos de processamento
- `AnalyticsAgent`: consolida metricas de adesao

### Tools

- `TelegramTool`
- `SupabaseTool`
- `TimeTool`
- `MessageTool`

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
.env.example
.gitignore
requirements.txt
render.yaml
README.md
```

## Modelo de dados

### Usuario

- `name`
- `telegram_chat_id`

### Reminder

- `title`
- `message`
- `hour`
- `minute`
- `days_of_week`
- `active`

### Reminder logs

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

`days_of_week` segue o padrao:
- `0` = segunda
- `1` = terca
- `2` = quarta
- `3` = quinta
- `4` = sexta
- `5` = sabado
- `6` = domingo

Se `days_of_week` nao for informado, o reminder vale para todos os dias.

## Variaveis de ambiente

Crie um `.env` com:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
TELEGRAM_BOT_TOKEN=
APP_BASE_URL=
APP_TIMEZONE=America/Sao_Paulo
SCHEDULER_TOKEN=
```

## Banco no Supabase

1. Crie um projeto no Supabase
2. Abra o `SQL Editor`
3. Rode o SQL de [app/sql/schema.sql](/c:/Users/leona/Documents/band-routine-assistant/app/sql/schema.sql:1)
4. Em `Project Settings > API`, copie:
- `Project URL` para `SUPABASE_URL`
- `service_role` para `SUPABASE_SERVICE_ROLE_KEY`

Se o banco ja existir:

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

## Scheduler operacional recomendado

O scheduler principal recomendado para operacao free e `cron-job.org`.

### Por que essa escolha

- gratuito
- confiavel para HTTP cron
- simples de configurar
- nao depende do `schedule` do GitHub Actions
- nao exige alterar a arquitetura da aplicacao

## Configuracao no cron-job.org

Crie um cron job com:

- URL: `https://miband-9-routine-assistant.onrender.com/scheduler/run`
- Method: `POST`
- Header: `X-Scheduler-Token: <SCHEDULER_TOKEN>`
- Frequencia: `every 5 minutes`

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

### Exemplo de resposta

```json
{
  "processed": 1,
  "sent_keys": ["reminder-id:202606051000"],
  "current_time": "2026-06-05T10:03:12-03:00",
  "window_minutes": 5
}
```

### Exemplo manual

```bash
curl -X POST "$APP_BASE_URL/scheduler/run" \
  -H "X-Scheduler-Token: $SCHEDULER_TOKEN"
```

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
- valide `GET /health`
- valide `GET /docs`
- valide manualmente `POST /scheduler/run`
- conecte o `cron-job.org`

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

## Operacao

### Checklist de producao minima

- Render online
- Supabase configurado
- bot do Telegram criado
- webhook do Telegram configurado
- usuario com `telegram_chat_id`
- reminders ativos
- `cron-job.org` chamando `/scheduler/run`

### Observabilidade

O endpoint `/scheduler/run` retorna:
- quantidade processada
- chaves enviadas
- horario atual
- janela de processamento

Isso permite diagnosticar rapidamente:
- se o scheduler chamou a API
- se havia reminders elegiveis
- se a janela operacional esta correta

## Qualidade

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
- seguranca basica e arquivos de ambiente

## Seguranca

- nao hardcode tokens ou chaves
- mantenha `.env` fora do versionamento
- use `SUPABASE_SERVICE_ROLE_KEY` apenas no backend
- proteja `/scheduler/run` com `SCHEDULER_TOKEN`
- nao exponha segredos em frontend, prints ou logs externos

## Limitacoes atuais

- a Mi Band depende do espelhamento de notificacoes do iPhone
- o projeto nao conversa diretamente com a pulseira
- o Render free pode sofrer cold start
- a confiabilidade do scheduler depende do servico HTTP externo escolhido

## Roadmap comercial

- painel admin para usuarios e agendas
- programas prontos de rotina e treino
- segmentacao por usuario e plano
- retries e alertas operacionais
- dashboard de adesao
- multi-tenant e billing

## Licenca

Defina a licenca conforme a estrategia comercial do produto.
