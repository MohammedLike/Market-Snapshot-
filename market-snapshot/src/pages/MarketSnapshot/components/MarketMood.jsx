import React from 'react'
import { motion } from 'framer-motion'

export default function MarketMood({ data }) {
  const { aiMood } = data
  if (!aiMood) return null

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ 
        background: 'var(--bg-card)', 
        border: `2px solid ${aiMood.color}`,
        borderRadius: 8,
        padding: '12px 20px',
        marginBottom: 16,
        display: 'flex',
        alignItems: 'center',
        gap: 15,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* AI Glow Effect */}
      <div style={{ 
        position: 'absolute', 
        top: 0, left: 0, bottom: 0, 
        width: 4, 
        background: aiMood.color,
        boxShadow: `0 0 10px ${aiMood.color}`
      }} />

      <div style={{ flexShrink: 0 }}>
        <div style={{ fontSize: 9, fontWeight: 900, opacity: 0.5, letterSpacing: 1 }}>AI MARKET MOOD</div>
        <div style={{ fontSize: 16, fontWeight: 900, color: aiMood.color }}>{aiMood.headline}</div>
      </div>

      <div style={{ 
        fontSize: 12, 
        lineHeight: 1.5, 
        color: 'var(--text-main)', 
        fontWeight: 500,
        opacity: 0.9,
        borderLeft: '1px solid var(--border-muted)',
        paddingLeft: 15
      }}>
        {aiMood.summary}
      </div>

      <div style={{ marginLeft: 'auto', fontSize: 20, opacity: 0.8 }}>
        🤖
      </div>
    </motion.div>
  )
}
