import asyncio
from config import TRADE_VOLUME_BTC
from .calculator import calculate_opportunity
from models.schemas import OrderBook, ArbitrageOpportunity
from typing import Callable, Optional

class ArbitrageDetector:
    """
    Compara orderbooks de dos exchanges y detecta oportunidades.
    Se llama en cada update de cualquier exchange.
    """
    def __init__(self, on_opportunity: Callable):
        self.orderbooks: dict[str, OrderBook] = {}
        self.on_opportunity = on_opportunity

    async def on_orderbook_update(self, exchange: str, ob: OrderBook):
        self.orderbooks[exchange] = ob
        if len(self.orderbooks) < 2:
            return
        exchanges = list(self.orderbooks.keys())
        # Probar ambas direcciones
        for buy_ex, sell_ex in [(exchanges[0], exchanges[1]),
                                 (exchanges[1], exchanges[0])]:
            opp = calculate_opportunity(
                buy_ob     = self.orderbooks[buy_ex],
                sell_ob    = self.orderbooks[sell_ex],
                volume_btc = TRADE_VOLUME_BTC
            )
            if opp:
                await self.on_opportunity(opp)
