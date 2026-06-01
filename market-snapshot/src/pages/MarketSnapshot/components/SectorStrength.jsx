import React from 'react'
import { motion } from 'framer-motion'

export default function SectorStrength({ data }) {
  const { sectors } = data

  return (
    <div className="section-block">
      <div className="section-label">{sectors.title}</div>
      <div className="sector-pills">
        {sectors.list.map((s, i) => (
          <motion.span
            key={s}
            className="sector-pill"
            initial={{ opacity: 0, scale: 0.88 }}
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
