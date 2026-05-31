export default function TradeHistory({ trades }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 h-64 overflow-y-auto border border-gray-800">
      <h2 className="text-sm text-gray-400 uppercase mb-3 font-bold">Historial de Trades</h2>
      <div className="space-y-2">
        {trades.length === 0 && (
          <div className="text-gray-600 text-xs italic text-center py-10">
            No se han ejecutado trades aún.
          </div>
        )}
        {trades.map((t, i) => (
          <div key={i} className="pb-2 border-b border-gray-800 last:border-0">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-300">
                {t.buy_exchange} → {t.sell_exchange}
              </span>
              <span className={`text-xs font-mono font-bold ${t.net_profit_usd >= 0 ? "text-green-400" : "text-red-400"}`}>
                {t.net_profit_usd >= 0 ? "+" : ""}${t.net_profit_usd.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-[10px] text-gray-500 mt-0.5">
              <span>{t.volume_btc} BTC @ ${t.buy_price.toLocaleString()}</span>
              <span>{new Date(t.executed_at).toLocaleTimeString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
