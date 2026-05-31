import React from 'react'
import { motion } from 'framer-motion'

export default function NiftyOutlook({ data }) {
  const { niftyOutlook } = data
  const { title, body, levels } = niftyOutlook

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 }}
    >
      <div className="card-label">NIFTY 50 PERFORMANCE</div>
      <h3 className="card-headline">{title}</h3>
      <p className="card-body" style={{ marginBottom: 14 }}>{body}</p>
      <div className="outlook-grid">
        {levels.map((lv) => (
          <div key={lv.label} className="outlook-cell" style={{ borderColor: lv.color + '55' }}>
            <span className="outlook-cell-label">{lv.label}</span>
            <span className="outlook-cell-value" style={{ color: lv.color }}>{lv.value}</span>
            <span className="outlook-cell-sub">{lv.sub}</span>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
