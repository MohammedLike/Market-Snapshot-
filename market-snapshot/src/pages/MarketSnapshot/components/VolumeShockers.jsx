import React from 'react'
import { motion } from 'framer-motion'

export default function VolumeShockers({ data }) {
  const { volumeShockers } = data

  return (
    <div>
      <div className="card-label" style={{ marginBottom: 8 }}>VOLUME SHOCKERS</div>
      {volumeShockers.map((item, i) => (
        <motion.div
          key={item.name}
          className="shocker-row"
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.05 * i }}
        >
          <span className="dot dot-green" />
          <span className="shocker-name">{item.name}</span>
          <span className="badge badge-green">{item.tag}</span>
        </motion.div>
      ))}
    </div>
  )
}
