from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, Float, Boolean, DateTime
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./arbitrage.db"
engine = create_async_engine(DATABASE_URL, echo=False)

class Base(DeclarativeBase): pass

class OpportunityRecord(Base):
    __tablename__ = "opportunities"
    id:             Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)
    buy_exchange:   Mapped[str]   = mapped_column(String)
    sell_exchange:  Mapped[str]   = mapped_column(String)
    buy_price:      Mapped[float] = mapped_column(Float)
    sell_price:     Mapped[float] = mapped_column(Float)
    gross_spread_pct: Mapped[float] = mapped_column(Float)
    net_profit_pct: Mapped[float] = mapped_column(Float)
    net_profit_usd: Mapped[float] = mapped_column(Float)
    executable:     Mapped[bool]  = mapped_column(Boolean)
    detected_at:    Mapped[datetime] = mapped_column(DateTime)

class TradeRecord(Base):
    __tablename__ = "trades"
    id:             Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)
    buy_exchange:   Mapped[str]   = mapped_column(String)
    sell_exchange:  Mapped[str]   = mapped_column(String)
    buy_price:      Mapped[float] = mapped_column(Float)
    sell_price:     Mapped[float] = mapped_column(Float)
    volume_btc:     Mapped[float] = mapped_column(Float)
    net_profit_usd: Mapped[float] = mapped_column(Float)
    net_profit_pct: Mapped[float] = mapped_column(Float)
    executed_at:    Mapped[datetime] = mapped_column(DateTime)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
