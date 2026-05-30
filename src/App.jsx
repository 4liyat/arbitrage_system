import { useState, useCallback, useEffect } from "react"
import { useWebSocket } from "./hooks/useWebSocket"
import OrderBook       from "./components/OrderBook"
import OpportunityFeed from "./components/OpportunityFeed"
import TradeHistory    from "./components/TradeHistory"
import PnLChart        from "./components/PnLChart"
import WalletStatus    from "./components/WalletStatus"

const API = import.meta.env.VITE_API_URL || "localhost:8000"
const WS_URL = `ws://${API}/ws`

export default function App() {
  const [orderbooks, setOrderbooks]     = useState({})
  const [opportunities, setOpportunities] = useState([])
  const [trades, setTrades]             = useState([])
  const [pnl, setPnl]                   = useState(0)
  const [wallets, setWallets]            = useState({})
  const [circuitBreakerStatus, setCircuitBreakerStatus] = useState(null)
  const [latency, setLatency] = useState(null)

  // Cargar historial al iniciar
  useEffect(() => {
    fetch(`http://${API}/api/trades`).then(r => r.json()).then(setTrades)
    fetch(`http://${API}/api/wallets`).then(r => r.json()).then(setWallets)
    fetch(`http://${API}/api/pnl`).then(r => r.json()).then(d => setPnl(d.total_pnl_usd))
  }, [])

  const onMessage = useCallback((msg) => {
    if (msg.type === "orderbook") {
      setOrderbooks(prev => ({ ...prev, [msg.exchange]: msg.data }))
    } else if (msg.type === "opportunity") {
      setOpportunities(prev => [msg.data, ...prev].slice(0, 100))
      // Calculate latency (S4 suggestion)
      const now = Date.now()
      const detected = new Date(msg.data.detected_at).getTime()
      setLatency(now - detected);
    } else if (msg.type === "trade") {
      setTrades(prev => [msg.data, ...prev])
      setPnl(prev => prev + msg.data.net_profit_usd)
      setWallets(msg.data.wallets_after)
    } else if (msg.type === "blocked") {
      setCircuitBreakerStatus(msg.reason);
    }
  }, [])

  useWebSocket(WS_URL, onMessage)

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-mono p-4">
      <header className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-white">BTC Arbitrage Monitor</h1>
          <p className="text-gray-400 text-sm">Binance ↔ Coinbase · Simulación en tiempo real</p>
        </div>
        <div className="flex items-center space-x-4">
          {circuitBreakerStatus && (
            <span className="text-xs text-amber-400 bg-amber-950 px-3 py-1 rounded-full border border-amber-700">
              ⚡ {circuitBreakerStatus}
            </span>
          )}
          <span className="text-xs text-gray-500">
            Latencia: {latency ? `${latency}ms` : "—"}
          </span>
        </div>
      </header>
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-5"><OrderBook orderbooks={orderbooks} /></div>
        <div className="col-span-4"><OpportunityFeed opportunities={opportunities} /></div>
        <div className="col-span-3"><WalletStatus wallets={wallets} pnl={pnl} /></div>
        <div className="col-span-8"><PnLChart trades={trades} /></div>
        <div className="col-span-4"><TradeHistory trades={trades} /></div>
      </div >
    </div >
  )
}
