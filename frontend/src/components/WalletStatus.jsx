export default function WalletStatus({ wallets, pnl }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 border border-gray-800 h-full">
      <h2 className="text-sm text-gray-400 uppercase mb-3 font-bold text-center">Estado de Balance</h2>
      
      <div className="text-center py-4 mb-4 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className={`text-3xl font-mono font-bold ${pnl >= 0 ? "text-green-400" : "text-red-400"}`}>
          {pnl >= 0 ? "+" : ""}${pnl.toFixed(2)}
        </div>
        <div className="text-[10px] text-gray-500 uppercase tracking-widest mt-1">P&L Total Estimado</div>
      </div>

      <div className="space-y-4">
        {Object.entries(wallets).length === 0 && (
          <div className="text-gray-600 text-xs text-center">Cargando balances...</div>
        )}
        {Object.entries(wallets).map(([exchange, balances]) => (
          <div key={exchange} className="bg-gray-950/50 p-3 rounded-lg border border-gray-800">
            <div className="text-[10px] text-gray-500 uppercase font-bold mb-2 flex justify-between items-center">
              <span>{exchange}</span>
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
            </div>
            <div className="space-y-1">
              {Object.entries(balances).map(([currency, amount]) => (
                <div key={currency} className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">{currency}</span>
                  <span className="text-xs font-mono text-white font-medium">
                    {typeof amount === "number" 
                      ? currency === "BTC" ? amount.toFixed(6) : amount.toLocaleString(undefined, {minimumFractionDigits: 2})
                      : amount}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
