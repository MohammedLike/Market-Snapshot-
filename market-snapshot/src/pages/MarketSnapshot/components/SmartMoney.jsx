import React from 'react'
import { motion } from 'framer-motion'

export default function SmartMoney({ data }) {
  const { smartMoney } = data
  const { title, longBuildup, shortBuildup, fiiLongShortRatio } = smartMoney
  const { shortPct, note } = fiiLongShortRatio

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 }}
    >
      <div className="card-label">{title}</div>

      <div className="smart-row">
        <span className="dot dot-green" />
        <span className="smart-label">{longBuildup.label}</span>
        <span className="smart-stocks" style={{ color: '#22C55E' }}>{longBuildup.stocks}</span>
      </div>
      <div className="smart-row" style={{ marginTop: 8 }}>
        <span className="dot dot-red" />
        <span className="smart-label">{shortBuildup.label}</span>
        <span className="smart-stocks" style={{ color: '#EF4444' }}>{shortBuildup.stocks}</span>
      </div>

      <div className="oi-section-label" style={{ marginTop: 16 }}>FII LONG-SHORT RATIO</div>
      <div className="smart-ratio-label">SHORT %</div>
      <div className="oi-bar-track" style={{ marginTop: 4 }}>
        <motion.div
          className="oi-bar-fill"
          style={{ background: '#EF4444' }}
          initial={{ width: 0 }}
          animate={{ width: `${shortPct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      <div className="smart-pct">{shortPct}%</div>
      <p className="card-note" style={{ marginTop: 6 }}>{note}</p>
    </motion.div>
  )
}
