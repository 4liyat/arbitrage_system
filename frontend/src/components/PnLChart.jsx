import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer, CartesianGrid } from "recharts"

export default function PnLChart({ trades }) {
  let cumulative = 0
  const data = trades.slice().reverse().map((t, i) => {
    cumulative += t.net_profit_usd
    return { 
      trade: i + 1, 
      pnl: Number(cumulative.toFixed(4)),
      time: new Date(t.executed_at).toLocaleTimeString()
    }
  })

  return (
    <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
      <h2 className="text-sm text-gray-400 uppercase mb-3 font-bold">Curva de P&L (USD)</h2>
      {data.length === 0 ? (
        <div className="h-[200px] flex items-center justify-center text-gray-600 text-sm italic">
          Esperando primer trade para generar gráfica...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
            <XAxis 
              dataKey="trade" 
              stroke="#4B5563" 
              fontSize={10} 
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#4B5563" 
              fontSize={10} 
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `$${value}`}
            />
            <Tooltip
              contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8, fontSize: '10px' }}
              itemStyle={{ color: "#10B981" }}
              labelStyle={{ color: "#9CA3AF" }}
              formatter={(v) => [`$${v}`, "P&L Acumulado"]}
              labelFormatter={(label, payload) => payload[0] ? `Trade #${label} - ${payload[0].payload.time}` : `Trade #${label}`}
            />
            <ReferenceLine y={0} stroke="#4B5563" strokeWidth={1} />
            <Line 
              type="monotone" 
              dataKey="pnl" 
              stroke="#10B981" 
              dot={{ r: 2, fill: "#10B981" }} 
              activeDot={{ r: 4 }}
              strokeWidth={2}
              animationDuration={500}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
