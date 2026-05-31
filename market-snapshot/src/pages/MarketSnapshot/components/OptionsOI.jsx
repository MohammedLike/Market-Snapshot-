import React from 'react'
import { motion } from 'framer-motion'

const levelColor = { Low: '#22C55E', Med: '#F59E0B', High: '#F97316', MAX: '#EF4444' }

function OIBar({ strike, level, pct, color }) {
  return (
    <div className="oi-row">
      <span className="oi-strike">{strike}</span>
      <div className="oi-bar-track">
        <motion.div
          className="oi-bar-fill"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
        />
      </div>
      <span className="oi-level" style={{ color }}>{level}</span>
    </div>
  )
}

export default function OptionsOI({ data }) {
  const { optionsOI } = data
  const { title, callOI, putOI, callWall, putFloor, note } = optionsOI

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="card-label">OPTIONS OI</div>
      <h3 className="card-headline">{title}</h3>

      <div className="oi-section-label">CALL OI (RESISTANCE)</div>
      {callOI.map((row) => (
        <OIBar key={row.strike} {...row} color={levelColor[row.level]} />
      ))}

      <div className="oi-section-label" style={{ marginTop: 12 }}>PUT OI (SUPPORT)</div>
      {putOI.map((row) => (
        <OIBar key={row.strike} {...row} color={levelColor[row.level]} />
      ))}

      <div className="oi-wall-row">
        <div className="oi-wall-box">
          <span className="oi-wall-label">CALL WALL</span>
          <span className="oi-wall-value" style={{ color: '#EF4444' }}>{callWall.toLocaleString()}</span>
        </div>
        <div className="oi-wall-box">
          <span className="oi-wall-label">PUT FLOOR</span>
          <span className="oi-wall-value" style={{ color: '#22C55E' }}>{putFloor.toLocaleString()}</span>
        </div>
      </div>

      <p className="card-note">{note}</p>
    </motion.div>
  )
}
