# band-routine-assistant

`band-routine-assistant` e um backend para orquestrar lembretes recorrentes via Telegram, com resposta em um toque, rastreabilidade operacional e base analitica para produtos de rotina, wellness e accountability.

O projeto foi desenhado para ser simples de operar, facil de evoluir e pronto para uso como fundacao de um produto comercial.

## Visao geral

O sistema executa um fluxo enxuto:
- um scheduler HTTP externo aciona a API
- a API identifica lembretes elegiveis por horario e dia da semana
- o Telegram entrega a notificacao ao usuario
- a resposta do usuario e registrada para acompanhamento e analytics

## O que o produto entrega

- Lembretes recorrentes com baixo atrito
- Resposta direta no Telegram com botoes inline
- Registro de `done`, `not_done` e `postponed`
- Regras por horario e dia da semana
- Estrutura pronta para auditoria, observabilidade e metricas
- Arquitetura modular para evolucao comercial

## Casos de uso

- Rotinas pessoais e micro-habitos
- Programas de treino e adesao
- Check-ins de autocuidado
- Fluxos de accountability
- MVPs wellness e health behavior

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

## Arquitetura

O projeto separa claramente regra de negocio, orquestracao e execucao tecnica.

- `Agent`: coordena responsabilidade de negocio
- `Tool`: executa acao tecnica reutilizavel
- `Service`: encapsula integracoes externas

### Agents

- `OrchestratorAgent`
- `SchedulerAgent`
- `ReminderAgent`
- `NotificationAgent`
- `LoggingAgent`
- `AnalyticsAgent`

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
  agents/
  tools/
  services/
  sql/
tests/
.env.example
.gitignore
requirements.txt
render.yaml
README.md
LICENSE
```

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

## Scheduler recomendado

O projeto foi estruturado para operar com scheduler HTTP externo. Para operacao simples e custo baixo, a estrategia recomendada e usar um serviço de cron HTTP como `cron-job.org`.

Essa abordagem:
- remove dependencia de scheduler interno na aplicacao
- reduz complexidade operacional
- funciona bem em deploys leves e ambientes de MVP

## Deploy

O projeto inclui configuracao de deploy para Render em [render.yaml](/c:/Users/leona/Documents/band-routine-assistant/render.yaml:1).

O fluxo de deploy esperado e:
- publicar a API
- configurar variaveis de ambiente
- apontar o scheduler externo para o endpoint de processamento
- configurar o webhook do Telegram

Detalhes sensiveis de infraestrutura, credenciais e banco devem permanecer fora deste README e ser gerenciados via ambiente e documentacao interna de operacao.

## Operacao

O endpoint de scheduler retorna metadados suficientes para observacao operacional, incluindo quantidade processada, horario da execucao e identificadores enviados. Isso facilita diagnostico de:
- scheduler chamando a API
- existencia de reminders elegiveis
- comportamento da janela de processamento

## Qualidade

O projeto possui suite automatizada cobrindo:
- health check
- usuarios
- reminders
- callbacks do Telegram
- analytics
- deduplicacao do scheduler
- filtro por dia da semana

Para executar os testes:

```powershell
pytest
```

## Seguranca

- nao hardcode segredos
- mantenha credenciais fora do versionamento
- use variaveis de ambiente para configuracao sensivel
- proteja endpoints operacionais com autenticacao adequada

## Roadmap

- painel administrativo
- templates de rotina
- segmentacao por usuario e plano
- retries e alertas operacionais
- dashboards de adesao
- suporte multi-tenant

## Licenca

Este projeto esta licenciado sob a [MIT License](/c:/Users/leona/Documents/band-routine-assistant/LICENSE:1).
