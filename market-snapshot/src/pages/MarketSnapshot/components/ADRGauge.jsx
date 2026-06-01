import React from 'react'

export default function ADRGauge({ data }) {
  const { advances } = data
  if (!advances) return null

  const { adv, dec, ratio, pct } = advances
  
  // Thermometer logic
  const fillWidth = `${pct}%`
  
  return (
    <div className="card" style={{ flex: 1 }}>
      <div className="card-label">MARKET BREADTH (NIFTY 500)</div>
      
      <div style={{ marginTop: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--brand-green)' }}>ADV: {adv}</span>
          <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--brand-red)' }}>DEC: {dec}</span>
        </div>
        
        {/* Thermometer / Gauge */}
        <div style={{ 
          height: 24, 
          background: 'var(--brand-red)', 
          borderRadius: 4, 
          overflow: 'hidden',
          display: 'flex',
          border: '1px solid var(--border-main)'
        }}>
          <div style={{ 
            width: fillWidth, 
            background: 'var(--brand-green)', 
            height: '100%',
            transition: 'width 0.8s ease-out',
            display: 'flex',
            alignItems: 'center',
            paddingLeft: 8
          }}>
             {pct > 15 && <span style={{ fontSize: 10, fontWeight: 900, color: '#fff' }}>{pct}%</span>}
          </div>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, alignItems: 'baseline' }}>
          <span style={{ fontSize: 10, opacity: 0.6, fontWeight: 700 }}>ADR RATIO</span>
          <span style={{ fontSize: 18, fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{ratio}</span>
        </div>
      </div>
    </div>
  )
}
