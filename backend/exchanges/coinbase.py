import websockets, json
import asyncio
from datetime import datetime
from .base import ExchangeClient
from models.schemas import OrderBook, OrderBookLevel

COINBASE_WS = "wss://advanced-trade-ws.coinbase.com"

SUBSCRIBE_MSG = json.dumps({
    "type": "subscribe",
    "product_ids": ["BTC-USD"],
    "channel": "level2"
})

class CoinbaseClient(ExchangeClient):
    def __init__(self):
        super().__init__("coinbase")
        self._bids: dict = {}   # price_str -> qty
        self._asks: dict = {}

    def _snapshot(self):
        bids = sorted([(float(p), float(q)) for p, q in self._bids.items() if float(q) > 0],
                      reverse=True)[:5]
        asks = sorted([(float(p), float(q)) for p, q in self._asks.items() if float(q) > 0])[:5]
        from config import ORDERBOOK_DEPTH
        return OrderBook(
            exchange="coinbase",
            symbol="BTC-USD",
            bids=[OrderBookLevel(price=p, quantity=q) for p, q in bids],
            asks=[OrderBookLevel(price=p, quantity=q) for p, q in asks],
            timestamp=datetime.utcnow()
        )

    async def connect(self):
        while True:
            try:
                async with websockets.connect(COINBASE_WS) as ws:
                    await ws.send(SUBSCRIBE_MSG)
                    async for msg in ws:
                        data = json.loads(msg)
                        channel = data.get("channel", "")
                        if channel == "l2_data":
                            for event in data.get("events", []):
                                if event["type"] == "snapshot":
                                    self._bids.clear()
                                    self._asks.clear()
                                for update in event.get("updates", []):
                                    side = update["side"]
                                    price = update["price_level"]
                                    qty = update["new_quantity"]
                                    if side == "bid":
                                        self._bids[price] = qty
                                    else:
                                        self._asks[price] = qty
                                if self._bids and self._asks:
                                    self.orderbook = self._snapshot()
                                    await self._notify()
            except Exception as e:
                print(f"Coinbase WS error: {e} — reconectando en 3s")
                await asyncio.sleep(3)
