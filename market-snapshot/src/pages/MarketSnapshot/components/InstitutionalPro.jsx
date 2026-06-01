import React from 'react'

export default function InstitutionalPro({ data }) {
  const { fiiRatio, deliveryStats } = data
  if (!fiiRatio || !deliveryStats) return null

  return (
    <div className="card">
      <div className="card-label">INSTITUTIONAL "PRO" DATA</div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: 20, marginTop: 12 }}>
        
        {/* Left: FII Ratio */}
        <div style={{ borderRight: '1px solid var(--border-muted)', paddingRight: 15 }}>
          <div style={{ fontSize: 10, fontWeight: 800, opacity: 0.6, marginBottom: 8 }}>FII INDEX L/S RATIO</div>
          <div style={{ height: 12, background: 'var(--brand-red)', borderRadius: 6, overflow: 'hidden', display: 'flex', border: '1px solid var(--border-main)' }}>
            <div style={{ width: `${fiiRatio.ratio * 100}%`, background: 'var(--brand-green)', height: '100%' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
             <span style={{ fontSize: 14, fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{Math.round(fiiRatio.ratio * 100)}% L</span>
             <span style={{ fontSize: 14, fontWeight: 900, fontFamily: 'JetBrains Mono' }}>{Math.round((1 - fiiRatio.ratio) * 100)}% S</span>
          </div>
          <div style={{ 
            fontSize: 9, 
            marginTop: 10, 
            padding: '6px', 
            background: 'var(--bg-secondary)', 
            borderRadius: 4, 
            fontWeight: 700,
            color: fiiRatio.label === 'BULLISH' ? 'var(--brand-green)' : 'var(--brand-red)',
            border: `1px solid ${fiiRatio.label === 'BULLISH' ? 'var(--brand-green)' : 'var(--brand-red)'}`
          }}>
            {fiiRatio.sentiment}
          </div>
        </div>

        {/* Right: Delivery Data */}
        <div>
          <div style={{ fontSize: 10, fontWeight: 800, opacity: 0.6, marginBottom: 8 }}>HIGH CONVICTION DELIVERY</div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <tbody>
              {deliveryStats.map((stock, i) => (
                <tr key={i} style={{ borderBottom: i === deliveryStats.length - 1 ? 'none' : '1px solid var(--border-muted)' }}>
                  <td style={{ fontSize: 10, fontWeight: 800, padding: '4px 0' }}>{stock.symbol}</td>
                  <td style={{ fontSize: 10, fontFamily: 'JetBrains Mono', padding: '4px 0', textAlign: 'right' }}>
                    {stock.delivery}%
                  </td>
                  <td style={{ textAlign: 'right', padding: '4px 0' }}>
                    {stock.tag === 'HIGH CONVICTION' && (
                      <span style={{ fontSize: 7, fontWeight: 900, color: 'var(--brand-green)', border: '1px solid var(--brand-green)', padding: '1px 3px', borderRadius: 2 }}>PRO BUY</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  )
}
