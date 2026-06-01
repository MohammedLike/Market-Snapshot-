import React from 'react'
import { motion } from 'framer-motion'

// Tag colour: BREAKOUT = green, BREAKDOWN = red, others = amber
function tagColor(tag) {
  const t = tag.toUpperCase()
  if (t === 'BREAKOUT' || t === 'DELIVERY SPIKE' || t === 'DELIVERY')
    return 'var(--brand-green)'
  if (t === 'BREAKDOWN' || t === 'REJECTION')
    return 'var(--brand-red)'
  return '#F59E0B'
}

export default function VolumeShockers({ data }) {
  const { volumeShockers } = data

  return (
    <div className="section-block">
      <div className="section-label">VOLUME SHOCKERS</div>
      {volumeShockers.map((item, i) => (
        <motion.div
          key={item.name}
          className="shocker-row"
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.05 * i }}
        >
          <span className="dot dot-green" />
          <span className="shocker-name">{item.name}</span>
          <span className="shocker-tag" style={{ color: tagColor(item.tag) }}>
            {item.tag}
          </span>
        </motion.div>
      ))}
    </div>
  )
}
