import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import TYPE_CHECKING

# Type checking for circular dependencies
if TYPE_CHECKING:
    from engine.detector import ArbitrageDetector
    from engine.executor import SimulatedExecutor
    from engine.circuit_breaker import CircuitBreaker
    from models.schemas import ArbitrageOpportunity

from models.db import init_db, engine, OpportunityRecord, TradeRecord
from models.schemas import ArbitrageOpportunity
from exchanges.binance  import BinanceClient
from exchanges.coinbase import CoinbaseClient
from engine.detector    import ArbitrageDetector
from engine.executor    import SimulatedExecutor
from engine.circuit_breaker import CircuitBreaker

# Global instances (must be initialized before lifespan)
executor = SimulatedExecutor()
breaker  = CircuitBreaker()
ws_clients: list[WebSocket] = []
detector_instance: ArbitrageDetector = None # Placeholder for detector instance

async def broadcast(data: dict):
    """Envía un mensaje a todos los clientes WebSocket conectados."""
    msg = json.dumps(data, default=str)
    # Usamos list() para evitar problemas de iteración al remover elementos
    for ws in list(ws_clients):
        try:
            await ws.send_text(msg)
        except Exception:
            ws_clients.remove(ws)

async def on_opportunity(opp: ArbitrageOpportunity):
    """
    Callback principal: Maneja la persistencia, chequeo de riesgo y ejecución de la oportunidad.
    """
    # 1. Broadcast Orderbook Update (S4 requirement)
    # Esto asegura que el frontend siempre tenga los datos de precios más recientes.
    if detector_instance:
        for ex_name, ob in detector_instance.orderbooks.items():
            if ob:
                await broadcast({
                    "type": "orderbook",
                    "exchange": ex_name,
                    "data": ob.model_dump()
                })

    # 2. Persistir oportunidad
    async with AsyncSession(engine) as session:
        session.add(OpportunityRecord(**opp.model_dump()))
        await session.commit()

    # 3. Broadcast Opportunity (para el feed)
    await broadcast({"type": "opportunity", "data": opp.model_dump()})

    if not opp.executable:
        return

    # 4. Circuit Breaker Check
    ok, reason = breaker.check(opp, executor.total_pnl)
    if not ok:
        await broadcast({"type": "blocked", "reason": reason})
        return

    # 5. Execute Trade
    result = executor.execute(opp)
    if result["status"] == "executed":
        # 6. Record Trade
        breaker.record_trade(opp)
        trade = result["trade"]
        async with AsyncSession(engine) as session:
            session.add(TradeRecord(
                buy_exchange=opp.buy_exchange, sell_exchange=opp.sell_exchange,
                buy_price=opp.buy_price, sell_price=opp.sell_price,
                volume_btc=opp.volume_btc,
                net_profit_usd=trade["net_profit_usd"], net_profit_pct=trade["net_profit_pct"],
                executed_at=opp.detected_at
            ))
            await session.commit()
        
        # 7. Broadcast Trade
        await broadcast({"type": "trade", "data": trade})

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de la base de datos
    await init_db()
    
    # Inicialización de clientes y detector
    binance  = BinanceClient()
    coinbase = CoinbaseClient()
    global detector_instance
    detector_instance = ArbitrageDetector(on_opportunity)
    
    # Configuración de callbacks
    binance.on_update(detector_instance.on_orderbook_update)
    coinbase.on_update(detector_instance.on_orderbook_update)

    # Iniciar tareas de conexión en segundo plano
    asyncio.create_task(binance.connect())
    asyncio.create_task(coinbase.connect())
    
    yield
    # Cleanup (optional)

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"])

@app.get("/api/trades")
async def get_trades():
    async with AsyncSession(engine) as s:
        result = await s.execute(select(TradeRecord).order_by(TradeRecord.id.desc()).limit(100))
        return [dict(r.__dict__) for r in result.scalars()]

@app.get("/api/opportunities")
async def get_opportunities():
    async with AsyncSession(engine) as s:
        result = await s.execute(select(OpportunityRecord).order_by(OpportunityRecord.id.desc()).limit(200))
        return [dict(r.__dict__) for r in result.scalars()]

@app.get("/api/wallets")
async def get_wallets():
    return executor.wallets

@app.get("/api/pnl")
async def get_pnl():
    return {"total_pnl_usd": executor.total_pnl, "trade_count": len(executor.trades)}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        # Mantener la conexión abierta
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        ws_clients.remove(ws)
