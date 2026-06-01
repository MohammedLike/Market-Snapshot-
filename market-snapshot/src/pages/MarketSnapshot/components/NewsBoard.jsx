import React from 'react'
import { motion } from 'framer-motion'

export default function NewsBoard({ data }) {
  const { news } = data

  return (
    <div className="section-block">
      <div className="section-label">KEY NEWS</div>
      {news.map((item, i) => (
        <motion.div
          key={`${item.company}-${i}`}
          className="news-row"
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.05 * i }}
        >
          <span className="news-company">{item.company}</span>
          <span className="news-headline">{item.headline}</span>
        </motion.div>
      ))}
    </div>
  )
}
