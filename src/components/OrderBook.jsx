export default function OrderBook({ orderbooks }) {
  const exchanges = ["binance", "coinbase"]

  // Helper function to find the best bid/ask across all exchanges
  const getBestSpread = (orderbooks) => {
    let bestBid = { price: 0, exchange: null };
    let bestAsk = { price: Infinity, exchange: null };

    // Find the highest bid (best buy price)
    for (const ex of exchanges) {
      const ob = orderbooks[ex];
      if (ob && ob.bids.length > 0) {
        const currentBid = ob.bids[0].price;
        if (currentBid > bestBid.price) {
          bestBid = { price: currentBid, exchange: ex };
        }
      }
    }

    // Find the lowest ask (best sell price)
    for (const ex of exchanges) {
      const ob = orderbooks[ex];
      if (ob && ob.asks.length > 0) {
        const currentAsk = ob.asks[0].price;
        if (currentAsk < bestAsk.price) {
          bestAsk = { price: currentAsk, exchange: ex };
        }
      }
    }

    return { bestBid, bestAsk };
  };

  const { bestBid, bestAsk } = getBestSpread(orderbooks);

  return (
    <div className="bg-gray-900 rounded-xl p-4 h-full">
      <h2 className="text-sm text-gray-400 uppercase mb-3">Order Book</h2>
      <div className="grid grid-cols-2 gap-4">
        {exchanges.map(ex => {
          const ob = orderbooks[ex]
          const isBestBid = bestBid.exchange === ex && ob && ob.bids.length > 0 && ob.bids[0].price === bestBid.price;
          const isBestAsk = bestAsk.exchange === ex && ob && ob.asks.length > 0 && ob.asks[0].price === bestAsk.price;

          return (
            <div key={ex}>
              <div className="text-xs text-gray-500 capitalize mb-1">{ex}</div>
              {ob ? (
                <>
                  {/* ASKS (Sell side - Red) */}
                  <div className="mb-2">
                    <div className="text-xs text-gray-500 mb-1">ASKS (Sell)</div>
                    {ob.asks.slice().reverse().map((a, i) => (
                      <div 
                        key={i} 
                        className={`flex justify-between text-xs ${
                          i === 0 && isBestAsk ? "text-yellow-300 font-bold bg-red-900/30" : "text-red-400"
                        }`}
                      >
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
                      <div 
                        key={i} 
                        className={`flex justify-between text-xs ${
                          i === 0 && isBestBid ? "text-yellow-300 font-bold bg-green-900/30" : "text-green-400"
                        }`}
                      >
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
