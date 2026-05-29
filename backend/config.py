EXCHANGES = {
    "binance": {
        "taker_fee": 0.001,
        "withdrawal_fee_btc": 0.0005,
        "slippage_per_level": 0.0005,
    },
    "coinbase": {
        "taker_fee": 0.006,
        "withdrawal_fee_btc": 0.0,
        "slippage_per_level": 0.001,
    },
}

MIN_NET_PROFIT_PCT = -0.05   # -5% mínimo para probar ejecutable
TRADE_VOLUME_BTC   = 0.01     # volumen por operación simulada
ORDERBOOK_DEPTH    = 5        # niveles a mantener
