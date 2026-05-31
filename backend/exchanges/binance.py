import websockets, json
import asyncio
from datetime import datetime
from .base import ExchangeClient
from models.schemas import OrderBook, OrderBookLevel

# Binance US-compliant or alternative global endpoint
BINANCE_WS = "wss://stream.binance.com:443/ws/btcusdt@depth5@100ms"

class BinanceClient(ExchangeClient):
    def __init__(self):
        super().__init__("binance")

    async def connect(self):
        while True:  # reconexión automática
            try:
                async with websockets.connect(BINANCE_WS, max_size=None) as ws:
                    async for msg in ws:
                        data = json.loads(msg)
                        self.orderbook = OrderBook(
                            exchange="binance",
                            symbol="BTC/USDT",
                            bids=[OrderBookLevel(price=float(b[0]), quantity=float(b[1]))
                                  for b in data["bids"]],
                            asks=[OrderBookLevel(price=float(a[0]), quantity=float(a[1]))
                                  for a in data["asks"]],
                            timestamp=datetime.utcnow()
                        )
                        await self._notify()
            except Exception as e:
                print(f"Binance WS error: {e} — reconectando en 3s")
                await asyncio.sleep(3)
