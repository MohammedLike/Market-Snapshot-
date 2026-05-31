import React from 'react'

export default function MarketTicker({ data }) {
  const { ticker } = data

  return (
    <div className="ticker-bar">
      <div className="ticker-inner">
        {ticker.map((item, i) => (
          <span key={i} className="ticker-item">
            <span className="ticker-label">{item.label}</span>
            <span
              className="ticker-value"
              style={{
                color: item.sign > 0 ? '#22C55E' : item.sign < 0 ? '#EF4444' : '#94A3B8',
              }}
            >
              {item.value}
            </span>
          </span>
        ))}
      </div>
    </div>
  )
}
