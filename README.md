# Shaqyru

Telegram bot collects data about users: name, city, phone. Then forwards it to group chat. Data is saved in google sheets and postgresql. App monitoring provided by Sentry.

shaqyru - word from Kazakh шақыру ("invite").

## Backend installation

1. Clone repository

```bash
git clone https://github.com/zshanabek/shaqyru
cd shaqyru
```

2. Install dependencies via `pipenv` package management system

```bash
pipenv install
```

3. Create the environment variables file named `.env`. In it write down token, Postgresql database connection credentials.

```text
ENV=DEVELOPMENT
PG_HOST=localhost
PG_DATABASE=<DATABASE>
PG_USER=<USER>
PG_PASSWORD=<PASSWORD>
BOT_TOKEN=<TOKEN>
GROUP_CHAT_ID=<CHAT_ID>
SHEET_ID=<SHEET_ID>
```

4. Run bot

```bash
python src/bot.py
```
