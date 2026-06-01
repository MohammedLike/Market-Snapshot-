import React from 'react'

export default function SectorHeatmap({ data }) {
  const { heatmap } = data
  if (!heatmap) return null

  // Treemap-like squares using CSS Grid
  return (
    <div className="card">
      <div className="card-label">SECTOR PERFORMANCE HEATMAP</div>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))', 
        gap: 6, 
        marginTop: 12 
      }}>
        {heatmap.map((sector) => (
          <div 
            key={sector.name}
            style={{
              padding: '10px 4px',
              borderRadius: 4,
              textAlign: 'center',
              background: sector.value >= 0 ? `rgba(22, 163, 74, ${Math.min(Math.abs(sector.value) * 0.4 + 0.1, 1)})` : `rgba(220, 38, 38, ${Math.min(Math.abs(sector.value) * 0.4 + 0.1, 1)})`,
              border: '1px solid var(--border-main)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center'
            }}
          >
            <span style={{ fontSize: 9, fontWeight: 900, color: '#fff', textTransform: 'uppercase' }}>{sector.name}</span>
            <span style={{ fontSize: 11, fontWeight: 800, color: '#fff', fontFamily: 'JetBrains Mono' }}>{sector.value > 0 ? '+' : ''}{sector.value}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
