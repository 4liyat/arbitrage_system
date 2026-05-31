export default function OpportunityFeed({ opportunities }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 h-80 overflow-y-auto border border-gray-800">
      <h2 className="text-sm text-gray-400 uppercase mb-3 font-bold flex justify-between">
        Oportunidades
        <span className="text-[10px] bg-gray-800 px-2 py-0.5 rounded text-gray-500">Live</span>
      </h2>
      <div className="space-y-2">
        {opportunities.length === 0 && (
          <div className="text-gray-600 text-xs italic text-center py-10">
            Esperando señales del mercado...
          </div>
        )}
        {opportunities.map((opp, i) => (
          <div key={i} className={`p-2 rounded text-xs border-l-2 transition-all ${
            opp.executable ? "border-green-500 bg-green-950/30" : "border-gray-700 bg-gray-800/50"
          }`}>
            <div className="flex justify-between items-center mb-1">
              <span className="text-gray-300 font-bold">
                {opp.buy_exchange.toUpperCase()} <span className="text-gray-600">→</span> {opp.sell_exchange.toUpperCase()}
              </span>
              <span className={`font-mono ${opp.executable ? "text-green-400" : "text-gray-500"}`}>
                {opp.net_profit_pct > 0 ? "+" : ""}{opp.net_profit_pct.toFixed(4)}%
              </span>
            </div>
            <div className="flex justify-between text-[10px] text-gray-500">
              <span>Compra: ${opp.buy_price.toLocaleString()}</span>
              <span>Venta: ${opp.sell_price.toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
