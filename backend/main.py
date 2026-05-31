import asyncio, json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
 
from models.db import init_db, engine, OpportunityRecord, TradeRecord
from models.schemas import ArbitrageOpportunity
from exchanges.binance  import BinanceClient
from exchanges.coinbase import CoinbaseClient
from engine.detector    import ArbitrageDetector
from engine.executor    import SimulatedExecutor
from engine.circuit_breaker import CircuitBreaker
 
executor = SimulatedExecutor()
breaker  = CircuitBreaker()
ws_clients: list[WebSocket] = []
 
async def broadcast(data: dict):
    msg = json.dumps(data, default=str)
    for ws in list(ws_clients):
        try: await ws.send_text(msg)
        except: ws_clients.remove(ws)
 
async def on_opportunity(opp: ArbitrageOpportunity):
    """
    Callback principal: Maneja la persistencia, chequeo de riesgo y ejecución de la oportunidad.
    Este método es llamado por el detector en cada update de orderbook.
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
    # Broadcast al frontend
    await broadcast({"type": "opportunity", "data": opp.model_dump()})
 
    if not opp.executable:
        return
 
    # 3. Circuit Breaker Check
    ok, reason = breaker.check(opp, executor.total_pnl)
    if not ok:
        await broadcast({"type": "blocked", "reason": reason})
        return
 
    # 4. Execute Trade
    result = executor.execute(opp)
    if result["status"] == "executed":
        # 5. Record Trade
        breaker.record_trade(opp)
        trade = result["trade"]
        async with AsyncSession(engine) as session:
            session.add(TradeRecord(
                buy_exchange=opp.buy_exchange, sell_exchange=opp.sell_exchange,
                buy_price=opp.buy_price, sell_price=opp.sell_price,
                volume_btc=opp.volume_btc,
                net_profit_usd=opp.net_profit_usd, net_profit_pct=opp.net_profit_pct,
                executed_at=opp.detected_at
            ))
            await session.commit()
        # 6. Broadcast Trade
        await broadcast({"type": "trade", "data": trade})
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    binance  = BinanceClient()
    coinbase = CoinbaseClient()
    global detector_instance
    detector_instance = ArbitrageDetector(on_opportunity)
    binance.on_update(detector_instance.on_orderbook_update)
    coinbase.on_update(detector_instance.on_orderbook_update)
    asyncio.create_task(binance.connect())
    asyncio.create_task(coinbase.connect())
    yield
 
app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"])
 
@app.get("/api/trades")
async def get_trades():
    """Obtiene los últimos 100 trades ejecutados."""
    async with AsyncSession(engine) as s:
        result = await s.execute(select(TradeRecord).order_by(TradeRecord.id.desc()).limit(100))
        return [dict(r.__dict__) for r in result.scalars()]
 
@app.get("/api/opportunities")
async def get_opportunities():
    """Obtiene los últimos 200 oportunidades detectadas."""
    async with AsyncSession(engine) as s:
        result = await s.execute(select(OpportunityRecord).order_by(OpportunityRecord.id.desc()).limit(200))
        return [dict(r.__dict__) for r in result.scalars()]
 
@app.get("/api/wallets")
async def get_wallets():
    """Devuelve el estado actual de las carteras simuladas."""
    return executor.wallets
 
@app.get("/api/pnl")
async def get_pnl():
    """Devuelve el P&L total y el conteo de trades."""
    return {"total_pnl_usd": executor.total_pnl, "trade_count": len(executor.trades)}
 
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Endpoint WebSocket para broadcast de datos en tiempo real."""
    await ws.accept()
    ws_clients.append(ws)
    try:
        # Mantener la conexión abierta
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        ws_clients.remove(ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
