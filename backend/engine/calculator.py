from config import EXCHANGES, MIN_NET_PROFIT_PCT
from models.schemas import OrderBook, ArbitrageOpportunity
from datetime import datetime

def calculate_opportunity(
    buy_ob: OrderBook,
    sell_ob: OrderBook,
    volume_btc: float
) -> ArbitrageOpportunity | None:
    """
    Calcula el profit neto de comprar en buy_ob y vender en sell_ob.
    Consume niveles del orderbook hasta cubrir volume_btc.
    Aplica: taker fee compra + venta + slippage + withdrawal fee.

    Args:
        buy_ob: OrderBook del exchange donde se compra (asks).
        sell_ob: OrderBook del exchange donde se vende (bids).
        volume_btc: Volumen de BTC a operar.

    Returns:
        ArbitrageOpportunity: Objeto con el cálculo de la oportunidad, o None si la liquidez es insuficiente.
    """
    buy_cfg  = EXCHANGES[buy_ob.exchange]
    sell_cfg = EXCHANGES[sell_ob.exchange]

    # Precio promedio ponderado de compra consumiendo niveles
    remaining = volume_btc
    buy_cost  = 0.0
    for level in buy_ob.asks:
        fill = min(remaining, level.quantity)
        buy_cost  += fill * level.price
        remaining -= fill
        if remaining <= 0:
            break
    if remaining > 0:
        return None  # liquidez insuficiente en asks

    remaining  = volume_btc
    sell_revenue = 0.0
    for level in sell_ob.bids:
        fill = min(remaining, level.quantity)
        sell_revenue += fill * level.price
        remaining    -= fill
        if remaining <= 0:
            break
    if remaining > 0:
        return None  # liquidez insuficiente en bids

    buy_price  = buy_cost  / volume_btc
    sell_price = sell_revenue / volume_btc

    gross_spread_pct = (sell_price - buy_price) / buy_price

    # Costos
    fee_buy       = buy_cost     * buy_cfg["taker_fee"]
    fee_sell      = sell_revenue * sell_cfg["taker_fee"]
    slippage_buy  = buy_cost     * buy_cfg["slippage_per_level"]
    slippage_sell = sell_revenue * sell_cfg["slippage_per_level"]
    withdrawal    = buy_cfg["withdrawal_fee_btc"] * sell_price

    total_cost   = buy_cost + fee_buy + slippage_buy + withdrawal
    total_revenue= sell_revenue - fee_sell - slippage_sell
    net_profit   = total_revenue - total_cost
    net_profit_pct = net_profit / total_cost
    net_profit_pct_val = round(net_profit_pct * 100, 4)
    executable = net_profit_pct_val >= MIN_NET_PROFIT_PCT * 100

    return ArbitrageOpportunity(
        buy_exchange   = buy_ob.exchange,
        sell_exchange  = sell_ob.exchange,
        buy_price      = round(buy_price, 2),
        sell_price     = round(sell_price, 2),
        gross_spread_pct = round(gross_spread_pct * 100, 4),
        net_profit_pct   = net_profit_pct_val,
        net_profit_usd   = round(net_profit, 4),
        volume_btc       = volume_btc,
        executable       = executable,
        detected_at      = datetime.utcnow()
    )

