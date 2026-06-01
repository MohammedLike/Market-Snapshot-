import React from 'react'

export default function GlobalAlignment({ data }) {
  const { globalAlignment } = data
  if (!globalAlignment) return null

  const { score, label, alignment } = globalAlignment
  
  return (
    <div className="card" style={{ background: 'var(--bg-secondary)', position: 'relative', overflow: 'hidden' }}>
      <div className="card-label">GLOBAL OPENING ALIGNMENT</div>
      
      <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 15 }}>
        <div style={{ position: 'relative', width: 50, height: 50, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <svg width="50" height="50" viewBox="0 0 36 36">
                <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="var(--border-muted)"
                    strokeWidth="3"
                />
                <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke={score > 70 ? 'var(--brand-green)' : '#F59E0B'}
                    strokeWidth="3"
                    strokeDasharray={`${score}, 100`}
                />
             </svg>
             <span style={{ position: 'absolute', fontSize: 11, fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{score}%</span>
        </div>
        
        <div>
            <div style={{ fontSize: 10, fontWeight: 900, color: score > 70 ? 'var(--brand-green)' : '#F59E0B' }}>
                {label}
            </div>
            <div style={{ fontSize: 9, opacity: 0.6, marginTop: 2 }}>{alignment}</div>
        </div>
      </div>

      <div style={{ fontSize: 8, opacity: 0.4, marginTop: 12, fontStyle: 'italic' }}>
        Opening confidence based on overnight global performance.
      </div>
    </div>
  )
}
