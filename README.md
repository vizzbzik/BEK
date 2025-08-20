
# BEK Crypto App (FastAPI + PostgreSQL)

Полноценное веб‑приложение: регистрация, вход, баланс, переводы, история переводов.

## Переменные окружения
- `DATABASE_URL` — строка подключения к PostgreSQL (Render): `postgresql://whome_user:w5O1SxiKRCIA9C4Coj0QDDmwSGd8oGBO@dpg-d2i2qlu3jp1c738v2f90-a/whome`
- `SECRET_KEY` — любая длинная случайная строка

## Локальный запуск
```bash
pip install -r requirements.txt
set DATABASE_URL=postgresql://whome_user:w5O1SxiKRCIA9C4Coj0QDDmwSGd8oGBO@dpg-d2i2qlu3jp1c738v2f90-a/whome
set SECRET_KEY=dev-secret
uvicorn app.main:app --reload
```

## Деплой на Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Env Vars: `DATABASE_URL`, `SECRET_KEY`
```
