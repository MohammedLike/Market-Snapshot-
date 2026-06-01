import React from 'react'
import { motion } from 'framer-motion'

const tagColors = {
  'RISK OFF SENTIMENT': '#EF4444',
  'WAR & ENERGY FOCUS': '#F97316',
  'GIFT NIFTY -165 PTS': '#8B5CF6',
}

export default function Header({ data, theme, onToggleTheme }) {
  const { date, dayLabel, riskTags } = data

  return (
    <motion.header
      className="snapshot-header"
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="header-left">
        <span className="header-brand">POST-MARKET CLOSING REPORT</span>
        <h1 className="header-title">Market Snapshot</h1>
        <h2 className="header-date">{date}</h2>
      </div>
      <div className="header-right">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 }}>
          <span className="header-day-label">{dayLabel}</span>
          <button 
            className="theme-toggle" 
            onClick={onToggleTheme}
            title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
          >
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
        <div className="header-tags">
          {riskTags.map((tag) => (
            <span
              key={tag}
              className="risk-tag"
              style={{ borderColor: tagColors[tag] || '#64748B', color: tagColors[tag] || '#94A3B8' }}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </motion.header>
  )
}
