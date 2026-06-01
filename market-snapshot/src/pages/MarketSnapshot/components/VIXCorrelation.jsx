import React from 'react'

export default function VIXCorrelation({ data }) {
  const { vixCorrelation } = data
  if (!vixCorrelation) return null

  const { correlation, note } = vixCorrelation
  
  return (
    <div className="card" style={{ background: 'var(--bg-secondary)' }}>
      <div className="card-label">NIFTY vs VIX CORRELATION</div>
      
      <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ 
            fontSize: 24, 
            fontWeight: 900, 
            fontFamily: 'JetBrains Mono',
            color: correlation < -0.7 ? 'var(--brand-green)' : 'inherit'
        }}>
            {correlation}
        </div>
        <div>
            <div style={{ fontSize: 10, fontWeight: 900, color: correlation < -0.7 ? 'var(--brand-green)' : 'var(--text-main)' }}>
                {note.toUpperCase()}
            </div>
            <div style={{ fontSize: 9, opacity: 0.5 }}>30-DAY STATISTICAL CORR</div>
        </div>
      </div>
    </div>
  )
}
