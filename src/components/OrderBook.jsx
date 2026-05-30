export default function OrderBook({ orderbooks }) {
  const exchanges = ["binance", "coinbase"]
  return (
    <div className="bg-gray-900 rounded-xl p-4 h-full">
      <h2 className="text-sm text-gray-400 uppercase mb-3">Order Book</h2>
      <div className="grid grid-cols-2 gap-4">
        {exchanges.map(ex => {
          const ob = orderbooks[ex]
          return (
            <div key={ex}>
              <div className="text-xs text-gray-500 capitalize mb-1">{ex}</div>
              {ob ? (
                <>
                  {/* ASKS (Sell side - Red) */}
                  <div className="mb-2">
                    <div className="text-xs text-gray-500 mb-1">ASKS (Sell)</div>
                    {ob.asks.slice().reverse().map((a, i) => (
                      <div key={i} className={`flex justify-between text-xs ${i === 0 ? "text-yellow-300 font-bold" : "text-red-400"}`}>
                        <span className="w-1/2">{a.price.toLocaleString()}</span>
                        <span className="w-1/2 text-right text-gray-500">{a.quantity.toFixed(4)}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="border-t border-gray-700 my-1"/>
                  
                  {/* BIDS (Buy side - Green) */}
                  <div className="mb-2">
                    <div className="text-xs text-gray-500 mb-1">BIDS (Buy)</div>
                    {ob.bids.map((b, i) => (
                      <div key={i} className={`flex justify-between text-xs ${i === 0 ? "text-yellow-300 font-bold" : "text-green-400"}`}>
                        <span className="w-1/2">{b.price.toLocaleString()}</span>
                        <span className="w-1/2 text-right text-gray-500">{b.quantity.toFixed(4)}</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : <div className="text-xs text-gray-600">Conectando...</div>}
            </div>
          )
        })}
      </div >
    </div>
  )
}
