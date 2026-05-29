from abc import ABC, abstractmethod
from models.schemas import OrderBook
import asyncio

class ExchangeClient(ABC):
    def __init__(self, name: str):
        self.name = name
        self.orderbook: OrderBook | None = None
        self._callbacks = []

    def on_update(self, callback):
        """Registrar función a llamar cuando el orderbook cambie"""
        self._callbacks.append(callback)

    async def _notify(self):
        for cb in self._callbacks:
            await cb(self.name, self.orderbook)

    @abstractmethod
    async def connect(self):
        """Conectar al WS y mantener el loop"""
        pass
