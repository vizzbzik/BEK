
# BEK Crypto App (FastAPI + PostgreSQL)

Полноценное веб‑приложение: регистрация, вход, баланс, переводы, история переводов.

## Переменные окружения
- `DATABASE_URL` — строка подключения к PostgreSQL (Render): `postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB?sslmode=require`
- `SECRET_KEY` — любая длинная случайная строка

## Локальный запуск
```bash
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/cryptodb
set SECRET_KEY=dev-secret
uvicorn app.main:app --reload
```

## Деплой на Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env Vars: `DATABASE_URL`, `SECRET_KEY`
```
