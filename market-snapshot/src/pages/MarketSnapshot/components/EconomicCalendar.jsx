import React from 'react'

export default function EconomicCalendar({ data }) {
  const { events } = data
  if (!events) return null

  return (
    <div className="card">
      <div className="card-label">UPCOMING ECONOMIC CALENDAR</div>
      
      <div style={{ marginTop: 12 }}>
        {events.map((item, i) => (
          <div 
            key={i} 
            style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              padding: '8px 0',
              borderBottom: i === events.length - 1 ? 'none' : '1px solid var(--border-muted)'
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: 10, fontWeight: 800 }}>{item.event}</span>
              <span style={{ fontSize: 9, opacity: 0.5 }}>{item.date}</span>
            </div>
            <span style={{ 
              fontSize: 8, 
              fontWeight: 900, 
              padding: '2px 5px', 
              borderRadius: 3,
              background: item.impact === 'HIGH' ? 'rgba(220, 38, 38, 0.1)' : 'rgba(249, 115, 22, 0.1)',
              color: item.impact === 'HIGH' ? 'var(--brand-red)' : '#F97316',
              border: `1px solid ${item.impact === 'HIGH' ? 'var(--brand-red)' : '#F97316'}`
            }}>
              {item.impact} IMPACT
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
