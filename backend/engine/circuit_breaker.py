from datetime import datetime, timedelta
from models.schemas import ArbitrageOpportunity

MAX_DRAWDOWN_PCT  = 0.05   # 5% pérdida máxima del capital inicial
COOLDOWN_SECONDS  = 30     # segundos entre operaciones del mismo par
INITIAL_CAPITAL   = 100_000.0  # USD total inicial estimado

class CircuitBreaker:
    def __init__(self):
        self._last_trade: dict[str, datetime] = {}
        self._triggered = False

    def check(self, opp: ArbitrageOpportunity, total_pnl: float) -> tuple[bool, str]:
        """Retorna (puede_ejecutar, motivo)"""
        if self._triggered:
            return False, "Circuit breaker activo — drawdown máximo alcanzado"

        # Drawdown check
        drawdown = -total_pnl / INITIAL_CAPITAL
        if drawdown > MAX_DRAWDOWN_PCT:
            self._triggered = True
            return False, f"Circuit breaker ACTIVADO: drawdown {drawdown:.2%}"

        # Cooldown check
        pair_key = f"{opp.buy_exchange}-{opp.sell_exchange}"
        if pair_key in self._last_trade:
            elapsed = (datetime.utcnow() - self._last_trade[pair_key]).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                return False, f"Cooldown activo para {pair_key}: {COOLDOWN_SECONDS - elapsed:.0f}s restantes"

        return True, "ok"

    def record_trade(self, opp: ArbitrageOpportunity):
        pair_key = f"{opp.buy_exchange}-{opp.sell_exchange}"
        self._last_trade[pair_key] = datetime.utcnow()

    def reset(self):
        self._triggered = False
        self._last_trade.clear()
