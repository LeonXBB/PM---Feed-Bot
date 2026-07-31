A Django web application and Telegram bot for managing (inputting, saving, displaying, and analyzing) sports events data, with scores, periods, and scheduled reminders. The web interface and bot run together and share a PostgreSQL database.

## Requirements

- Python 3.9 or later
- PostgreSQL
- A Telegram bot token

## Configuration

Create a `.env` file in the project root. Do not commit it: `.env` is already ignored by Git.

```env
django_key=replace-with-a-secret-django-key
django_debug_mode=True

postgres_user=postgres
postgres_password=replace-with-your-password
postgres_host=127.0.0.1
postgres_port=5432

telebot_token=replace-with-your-telegram-bot-token
telebot_parse_mode=HTML
telebot_connection_type=polling
telebot_scheduled_messages_update_interval=30
telebot_version=local

input_address=127.0.0.1
PORT=8000
output_protocol=http
output_address=127.0.0.1:8000
```

Create the PostgreSQL database named `postgres`, or update the database name in `feed_bot/meta/settings.py` to match your environment.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The entry point applies migrations, starts the Django development server, and launches the Telegram bot. With the example configuration, the web app is available at `http://127.0.0.1:8000`.

## Docker

Build and run the application with the environment values from `.env`:

```bash
docker build -t pm-feed-bot .
docker run --env-file .env -p 8000:80 pm-feed-bot
```

## Project layout

- `main.py` - starts the Django server and Telegram bot processes.
- `feed_bot/meta/` - Django settings, URLs, and ASGI/WSGI configuration.
- `feed_bot/tg_bot/` - Telegram bot logic, event models, screens, and reminders.
- `feed_bot/website/` - web views, templates, static assets, and WebSocket consumers.
