# Ejecutar con: python test_detector.py
# Debe mostrar oportunidades detectadas en consola
import asyncio
from exchanges.binance  import BinanceClient
from exchanges.coinbase import CoinbaseClient
from engine.detector    import ArbitrageDetector

async def on_opportunity(opp):
    tag = "✅ EJECUTABLE" if opp.executable else "  sub-threshold"
    print(f"{tag} | buy:{opp.buy_exchange} @{opp.buy_price:,.2f} sell:{opp.sell_exchange} @{opp.sell_price:,.2f} neto:{opp.net_profit_pct:.4f}%")

async def debug_callback(ex, ob):
    print(f"Update recibido de {ex} | Bids: {len(ob.bids)} Asks: {len(ob.asks)}")

async def main():
    print("Iniciando BinanceClient...")
    binance  = BinanceClient()
    print("Iniciando CoinbaseClient...")
    coinbase = CoinbaseClient()
    detector = ArbitrageDetector(on_opportunity)

    print("Configurando callbacks...")
    binance.on_update(debug_callback)
    coinbase.on_update(debug_callback)
    
    binance.on_update(detector.on_orderbook_update)
    coinbase.on_update(detector.on_orderbook_update)

    print("Conectando a los WebSockets...")
    await asyncio.gather(
        binance.connect(),
        coinbase.connect()
    )

if __name__ == "__main__":
    asyncio.run(main())
