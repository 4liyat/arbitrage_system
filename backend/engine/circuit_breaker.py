from datetime import datetime, timedelta
from models.schemas import ArbitrageOpportunity

MAX_DRAWDOWN_PCT  = 0.05   # 5% pérdida máxima del capital inicial
COOLDOWN_SECONDS  = 30     # segundos entre operaciones del mismo par
INITIAL_CAPITAL   = 100_000.0  # USD total inicial estimado

class CircuitBreaker:
    """
    Implementa lógica de gestión de riesgos para detener la ejecución de trades
    cuando se alcanza un drawdown máximo o se viola un periodo de cooldown.
    """
    def __init__(self):
        self._last_trade: dict[str, datetime] = {}
        self._triggered = False

    def check(self, opp: ArbitrageOpportunity, total_pnl: float) -> tuple[bool, str]:
        """
        Verifica si la operación puede ejecutarse según las reglas de riesgo.

        Args:
            opp: La oportunidad de arbitraje detectada.
            total_pnl: El P&L acumulado actual.

        Returns:
            tuple[bool, str]: (puede_ejecutar, motivo)
        """
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
        """Registra la ejecución de un trade para aplicar el cooldown."""
        pair_key = f"{opp.buy_exchange}-{opp.sell_exchange}"
        self._last_trade[pair_key] = datetime.utcnow()

    def reset(self):
        """Resetea el estado del Circuit Breaker."""
        self._triggered = False
        self._last_trade.clear()
