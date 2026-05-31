import React from 'react'
import { motion } from 'framer-motion'

function formatCr(val) {
  const abs = Math.abs(val)
  const sign = val < 0 ? '-' : '+'
  return `${sign}₹${abs.toLocaleString('en-IN')} cr`
}

export default function FIIDII({ data }) {
  const { fiiDii } = data
  const { fii, dii } = fiiDii

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="card-label">FII / DII CASH MARKET</div>
      <div className="fiidii-row">
        <div className="fiidii-box">
          <span className="fiidii-entity">FII</span>
          <span className="fiidii-value" style={{ color: fii.today < 0 ? '#EF4444' : '#22C55E' }}>
            {formatCr(fii.today)}
          </span>
          <span className="fiidii-mtd">{fii.mtdLabel}</span>
        </div>
        <div className="fiidii-box">
          <span className="fiidii-entity">DII</span>
          <span className="fiidii-value" style={{ color: dii.today > 0 ? '#22C55E' : '#EF4444' }}>
            {formatCr(dii.today)}
          </span>
          <span className="fiidii-mtd">{dii.mtdLabel}</span>
        </div>
      </div>
    </motion.div>
  )
}
