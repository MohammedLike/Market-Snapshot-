import React from 'react'
import { motion } from 'framer-motion'

export default function GlobalCues({ data }) {
  const { globalCues } = data
  const { headline, body, tags } = globalCues

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="card-label">GLOBAL CUES</div>
      <h3 className="card-headline">{headline}</h3>
      <p className="card-body">{body}</p>
      <div className="tag-row">
        {tags.map((t) => (
          <span key={t} className="badge badge-dark">{t}</span>
        ))}
      </div>
    </motion.div>
  )
}
