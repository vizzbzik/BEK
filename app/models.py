
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    address = Column(String(64), unique=True, index=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)

    user = relationship("User", back_populates="wallet")
    outgoing_transfers = relationship("Transfer", back_populates="from_wallet", foreign_keys="Transfer.from_wallet_id")
    incoming_transfers = relationship("Transfer", back_populates="to_wallet", foreign_keys="Transfer.to_wallet_id")

class Transfer(Base):
    __tablename__ = "transfers"
    id = Column(Integer, primary_key=True)
    from_wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True)
    to_wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    from_wallet = relationship("Wallet", foreign_keys=[from_wallet_id], back_populates="outgoing_transfers")
    to_wallet = relationship("Wallet", foreign_keys=[to_wallet_id], back_populates="incoming_transfers")
