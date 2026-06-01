import React from 'react'

const labelMap = {
    "^NSEI": "NIFTY 50",
    "^NSEBANK": "BANK NIFTY",
    "RELIANCE.NS": "RELIANCE",
    "TCS.NS": "TCS",
    "HDFCBANK.NS": "HDFC BANK"
}

export default function TechnicalMetrics({ data }) {
  const { technicalMetrics } = data
  if (!technicalMetrics) return null

  return (
    <div className="card">
      <div className="card-label">TECHNICAL DMA & RSI SCAN</div>
      
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 12 }}>
        <thead>
          <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border-muted)' }}>
            <th style={{ fontSize: 9, paddingBottom: 6, opacity: 0.6 }}>SYMBOL</th>
            <th style={{ fontSize: 9, paddingBottom: 6, opacity: 0.6 }}>50 DMA</th>
            <th style={{ fontSize: 9, paddingBottom: 6, opacity: 0.6 }}>200 DMA</th>
            <th style={{ fontSize: 9, paddingBottom: 6, opacity: 0.6 }}>RSI (14)</th>
            <th style={{ fontSize: 9, paddingBottom: 6, opacity: 0.6 }}>STATUS</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(technicalMetrics).map(([symbol, stats]) => (
            <tr key={symbol} style={{ borderBottom: '1px solid var(--border-muted)' }}>
              <td style={{ fontSize: 10, fontWeight: 800, padding: '8px 0' }}>{labelMap[symbol] || symbol}</td>
              <td style={{ fontSize: 10, fontFamily: 'JetBrains Mono', padding: '8px 0' }}>{stats.dma50}</td>
              <td style={{ fontSize: 10, fontFamily: 'JetBrains Mono', padding: '8px 0' }}>{stats.dma200}</td>
              <td style={{ 
                fontSize: 10, 
                fontFamily: 'JetBrains Mono', 
                padding: '8px 0',
                color: stats.rsi > 70 ? 'var(--brand-red)' : stats.rsi < 30 ? 'var(--brand-green)' : 'inherit',
                fontWeight: (stats.rsi > 70 || stats.rsi < 30) ? 800 : 400
              }}>
                {stats.rsi}
              </td>
              <td style={{ padding: '8px 0' }}>
                <span style={{ 
                  fontSize: 8, 
                  fontWeight: 900, 
                  padding: '2px 4px', 
                  borderRadius: 3,
                  background: stats.status === 'BULLISH' ? 'rgba(22, 163, 74, 0.1)' : stats.status === 'BEARISH' ? 'rgba(220, 38, 38, 0.1)' : 'var(--bg-secondary)',
                  color: stats.status === 'BULLISH' ? 'var(--brand-green)' : stats.status === 'BEARISH' ? 'var(--brand-red)' : 'var(--text-muted)',
                  border: `1px solid ${stats.status === 'BULLISH' ? 'var(--brand-green)' : stats.status === 'BEARISH' ? 'var(--brand-red)' : 'var(--border-muted)'}`
                }}>
                  {stats.crossover || stats.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
