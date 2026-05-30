from datetime import datetime
from models.schemas import ArbitrageOpportunity
from config import TRADE_VOLUME_BTC

INITIAL_WALLETS = {
    "binance":  {"BTC": 1.0, "USDT": 50_000.0},
    "coinbase": {"BTC": 1.0, "USD":  50_000.0},
}

class SimulatedExecutor:
    """
    Simula la ejecución de órdenes de arbitraje.
    Gestiona el estado de las carteras (wallets) y el P&L acumulado.
    """
    def __init__(self):
        self.wallets = {
            "binance":  {"BTC": 1.0, "USDT": 50_000.0},
            "coinbase": {"BTC": 1.0, "USD":  50_000.0},
        }
        self.trades = []       # historial completo de trades
        self.total_pnl = 0.0   # P&L acumulado en USD

    def _quote_currency(self, exchange: str) -> str:
        """Determina la moneda de quote (USDT o USD) para el exchange dado."""
        return "USDT" if exchange == "binance" else "USD"

    def can_execute(self, opp: ArbitrageOpportunity) -> tuple[bool, str]:
        """
        Verifica si hay suficiente liquidez en las carteras para ejecutar la operación.

        Returns:
            tuple[bool, str]: (puede_ejecutar, motivo_fallo)
        """
        buy_quote = self._quote_currency(opp.buy_exchange)
        cost = opp.buy_price * opp.volume_btc
        
        # Check buy side liquidity
        if self.wallets[opp.buy_exchange].get(buy_quote, 0) < cost:
            return False, f"Balance insuficiente en {opp.buy_exchange}: necesita {cost:.2f} {buy_quote}"
        
        # Check sell side liquidity
        if self.wallets[opp.sell_exchange].get("BTC", 0) < opp.volume_btc:
            return False, f"BTC insuficiente en {opp.sell_exchange}"
        
        return True, "ok"

    def execute(self, opp: ArbitrageOpportunity) -> dict:
        """
        Ejecuta la operación simulada, actualiza las carteras y registra el trade.

        Returns:
            dict: Resultado de la ejecución (status y trade data).
        """
        ok, reason = self.can_execute(opp)
        if not ok:
            return {"status": "rejected", "reason": reason}

        buy_quote  = self._quote_currency(opp.buy_exchange)
        sell_quote = self._quote_currency(opp.sell_exchange)

        cost_usd     = opp.buy_price  * opp.volume_btc
        revenue_usd  = opp.sell_price * opp.volume_btc

        # --- Actualizar wallets ---
        
        # 1. Compra (Buy): Gasta quote, recibe BTC
        self.wallets[opp.buy_exchange][buy_quote] -= cost_usd
        self.wallets[opp.buy_exchange]["BTC"]     += opp.volume_btc

        # 2. Venta (Sell): Gasta BTC, recibe quote
        self.wallets[opp.sell_exchange]["BTC"]       -= opp.volume_btc
        self.wallets[opp.sell_exchange][sell_quote]  += revenue_usd

        # 3. Actualizar PnL
        self.total_pnl += opp.net_profit_usd

        # Crear registro de trade
        trade = {
            "id":            len(self.trades) + 1,
            "buy_exchange":  opp.buy_exchange,
            "sell_exchange": opp.sell_exchange,
            "buy_price":     opp.buy_price,
            "sell_price":    opp.sell_price,
            "volume_btc":    opp.volume_btc,
            "net_profit_usd": round(opp.net_profit_usd, 4),
            "net_profit_pct": round(opp.net_profit_pct, 4),
            "wallets_after": {k: dict(v) for k, v in self.wallets.items()},
            "executed_at":   datetime.utcnow().isoformat(),
        }
        self.trades.append(trade)
        return {"status": "executed", "trade": trade}
