import React from 'react'
import { LineChart, Line, ResponsiveContainer, Tooltip, ReferenceLine } from 'recharts'
import { motion } from 'framer-motion'

export default function BrentCrude({ data }) {
  const { brentCrude } = data
  const { price, change, changeSign, prevLabel, resistance, note, sparkline } = brentCrude

  const chartData = sparkline.map((v, i) => ({ i, v }))

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="card-label">BRENT CRUDE</div>
      <div className="brent-top">
        <div>
          <span className="brent-price">${price.toFixed(2)}</span>
          <span
            className="brent-change"
            style={{ color: changeSign >= 0 ? '#22C55E' : '#EF4444' }}
          >
            {changeSign >= 0 ? '▲' : '▼'} {change}
          </span>
        </div>
        <span className="brent-prev">{prevLabel}</span>
      </div>

      <div className="brent-chart">
        <ResponsiveContainer width="100%" height={70}>
          <LineChart data={chartData}>
            <Line
              type="monotone"
              dataKey="v"
              stroke="#F97316"
              strokeWidth={2}
              dot={false}
            />
            <ReferenceLine y={resistance} stroke="#EF444466" strokeDasharray="3 3" />
            <Tooltip
              contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 6, fontSize: 11 }}
              formatter={(v) => [`$${v}`, 'Brent']}
              labelFormatter={() => ''}
            />
          </LineChart>
        </ResponsiveContainer>
        <span className="brent-resistance-label">RESISTANCE ${resistance}</span>
      </div>

      <p className="card-body" style={{ marginTop: 8 }}>{note}</p>
    </motion.div>
  )
}
