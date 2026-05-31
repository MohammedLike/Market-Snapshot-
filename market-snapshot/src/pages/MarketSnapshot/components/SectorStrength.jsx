import React from 'react'
import { motion } from 'framer-motion'

export default function SectorStrength({ data }) {
  const { sectors } = data

  return (
    <div style={{ marginTop: 20 }}>
      <div className="card-label" style={{ marginBottom: 8 }}>{sectors.title}</div>
      <div className="sector-badges">
        {sectors.list.map((s, i) => (
          <motion.span
            key={s}
            className="badge badge-sector"
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.05 * i }}
          >
            {s}
          </motion.span>
        ))}
      </div>
    </div>
  )
}
