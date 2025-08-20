
import os, secrets
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from .database import engine, Base, get_session
from .models import User, Wallet, Transfer

app = FastAPI(title="BEK Crypto App")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

SECRET_KEY = os.getenv("SECRET_KEY", "495d72d8937ca89286c37c77de249d10")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def current_user_id(request: Request):
    return request.session.get("user_id")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    uid = current_user_id(request)
    balance, address = None, None
    if uid:
        w = (await session.execute(select(Wallet).where(Wallet.user_id == uid))).scalar_one_or_none()
        if w:
            balance, address = w.balance, w.address
    return templates.TemplateResponse("index.html", {"request": request, "balance": balance, "address": address})

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_post(request: Request, email: str = Form(...), password: str = Form(...), confirm: str = Form(...), session: AsyncSession = Depends(get_session)):
    if password != confirm:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пароли не совпадают"})
    exists = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if exists:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})
    u = User(email=email, password_hash=pwd.hash(password))
    session.add(u)
    await session.flush()
    address = secrets.token_hex(20)
    w = Wallet(user_id=u.id, address=address, balance=0.0)
    session.add(w)
    await session.commit()
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, email: str = Form(...), password: str = Form(...), session: AsyncSession = Depends(get_session)):
    u = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not u or not pwd.verify(password, u.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный email или пароль"})
    request.session["user_id"] = u.id
    return RedirectResponse("/", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

@app.get("/balance", response_class=HTMLResponse)
async def balance_page(request: Request, session: AsyncSession = Depends(get_session)):
    uid = current_user_id(request)
    if not uid:
        return RedirectResponse("/login", status_code=303)
    w = (await session.execute(select(Wallet).where(Wallet.user_id == uid))).scalar_one_or_none()
    return templates.TemplateResponse("balance.html", {"request": request, "wallet": w})

@app.get("/transfer", response_class=HTMLResponse)
async def transfer_get(request: Request, session: AsyncSession = Depends(get_session)):
    uid = current_user_id(request)
    if not uid:
        return RedirectResponse("/login", status_code=303)
    w = (await session.execute(select(Wallet).where(Wallet.user_id == uid))).scalar_one_or_none()
    return templates.TemplateResponse("transfer.html", {"request": request, "wallet": w})

@app.post("/transfer", response_class=HTMLResponse)
async def transfer_post(request: Request, to_address: str = Form(...), amount: float = Form(...), session: AsyncSession = Depends(get_session)):
    uid = current_user_id(request)
    if not uid:
        return RedirectResponse("/login", status_code=303)
    from_wallet = (await session.execute(select(Wallet).where(Wallet.user_id == uid))).scalar_one_or_none()
    to_wallet = (await session.execute(select(Wallet).where(Wallet.address == to_address))).scalar_one_or_none()
    if not to_wallet:
        return templates.TemplateResponse("transfer.html", {"request": request, "wallet": from_wallet, "error": "Кошелёк получателя не найден"})
    if to_wallet.id == from_wallet.id:
        return templates.TemplateResponse("transfer.html", {"request": request, "wallet": from_wallet, "error": "Нельзя переводить самому себе"})
    if amount <= 0:
        return templates.TemplateResponse("transfer.html", {"request": request, "wallet": from_wallet, "error": "Сумма должна быть > 0"})
    if from_wallet.balance < amount:
        return templates.TemplateResponse("transfer.html", {"request": request, "wallet": from_wallet, "error": "Недостаточно средств"})
    from_wallet.balance -= amount
    to_wallet.balance += amount
    session.add(Transfer(from_wallet_id=from_wallet.id, to_wallet_id=to_wallet.id, amount=amount))
    await session.commit()
    w = (await session.execute(select(Wallet).where(Wallet.user_id == uid))).scalar_one_or_none()
    return templates.TemplateResponse("transfer.html", {"request": request, "wallet": w, "success": f"Успешно переведено {amount} BEK на {to_address}"})

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, session: AsyncSession = Depends(get_session)):
    uid = current_user_id(request)
    if not uid:
        return RedirectResponse("/login", status_code=303)
    w = (await session.execute(select(Wallet).where(Wallet.user_id == uid))).scalar_one_or_none()
    res = await session.execute(select(Transfer).where((Transfer.from_wallet_id == w.id) | (Transfer.to_wallet_id == w.id)).order_by(Transfer.created_at.desc()))
    txs = res.scalars().all()
    return templates.TemplateResponse("history.html", {"request": request, "wallet": w, "txs": txs})
