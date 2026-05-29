from pydantic import BaseModel
from typing import List, Tuple
from datetime import datetime

class OrderBookLevel(BaseModel):
    price: float
    quantity: float

class OrderBook(BaseModel):
    exchange: str
    symbol: str
    bids: List[OrderBookLevel]  # precio desc
    asks: List[OrderBookLevel]  # precio asc
    timestamp: datetime

class ArbitrageOpportunity(BaseModel):
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    gross_spread_pct: float
    net_profit_pct: float
    net_profit_usd: float
    volume_btc: float
    executable: bool
    detected_at: datetime
