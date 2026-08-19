# band-routine-assistant

`band-routine-assistant` is a FastAPI backend for habit reminders delivered directly to a Xiaomi Smart Band 9 Pro via Bluetooth Low Energy, with operational traceability and a lightweight analytics dashboard.

## Highlights

- Direct BLE notification delivery to Mi Band 9 Pro
- Habit response tracking with `done`, `not_done`, `postponed`, `sent`, and `error`
- Weekly schedule support with hour, minute, and day-of-week rules
- External HTTP scheduler support for lean deployments
- Web dashboard with summary metrics, activity charts, and recent logs
- Modular architecture with agents, tools, and services

## Product Flow

1. An external scheduler calls the API.
2. The API finds reminders that match the current time window.
3. BLE delivers the notification directly to the Mi Band 9 Pro.
4. The system records the result and updates analytics.

## Stack

- Python 3.11+
- FastAPI
- Jinja2
- Uvicorn
- Supabase Python Client
- PostgreSQL / Supabase
- Bleak (Bluetooth Low Energy)
- httpx
- python-dotenv
- pydantic-settings
- pytest
- pytest-asyncio

## Architecture

The project keeps business coordination separate from technical execution.

- `Agent`: business decision or orchestration layer
- `Tool`: reusable technical action
- `Service`: external integration wrapper

### Agents

- `OrchestratorAgent`
- `SchedulerAgent`
- `ReminderAgent`
- `NotificationAgent`
- `LoggingAgent`
- `AnalyticsAgent`

### Tools

- `SupabaseTool`
- `TimeTool`
- `MessageTool`

### Notifications

- `NotificationTransport` (ABC)
- `BLETransport`
- `NotificationService`

### Miband BLE

- `MiBandClient`
- `ConnectionManager`
- `MiBandProtocol`
- `scanner`

## Main Endpoints

- `GET /health`
- `POST /users`
- `GET /users`
- `POST /reminders`
- `GET /reminders`
- `PATCH /reminders/{id}/toggle`
- `GET /analytics`
- `POST /scheduler/run`
- `GET /dashboard`
- `GET /api/dashboard/metrics`

## Dashboard

The project includes a responsive glassmorphism dashboard for tracking habit consistency and reminder outcomes.

### Access

- Web page: `GET /dashboard`
- JSON metrics: `GET /api/dashboard/metrics`

### Dashboard Experience

- Executive summary cards
- Overall completion chart
- Activity-level performance cards
- Recent response log table
- Mobile-friendly layout

## Scheduler Strategy

The recommended setup is an external HTTP scheduler such as `cron-job.org` calling:

- `POST /scheduler/run`

This keeps the application simple, lightweight, and compatible with small-footprint deployments.

## BLE Setup

1. Install bleak: `pip install bleak`
2. Configure `.env`:
   ```
   MIBAND_BLE_ADDRESS=XX:XX:XX:XX:XX:XX
   MIBAND_BLE_NAME=Xiaomi Smart Band 9 Pro
   ```
3. Scan for devices: `python -m app.miband`
4. Inspect GATT: `python -m app.miband.inspect --output logs/miband_gatt.json`

## Local Development

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Test Suite

```powershell
pytest
```

## Project Structure

```text
app/
  agents/
  miband/
  notifications/
  routes/
  services/
  static/
  templates/
  tools/
  sql/
  main.py
  config.py
  database.py
  models.py
tests/
scripts/
.env.example
.gitignore
requirements.txt
render.yaml
LICENSE
README.md
```

## Quality

The automated suite covers:

- health checks
- users
- reminders
- analytics summaries
- dashboard metrics
- scheduler authentication and processing
- day-of-week filtering

## Security

- Keep credentials outside version control
- Use environment variables for sensitive configuration
- Protect operational endpoints with a scheduler token
- Keep database and infrastructure secrets in secure environment storage

## License

This project is licensed under the [MIT License](LICENSE).
