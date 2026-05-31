import React from 'react'

export default function IndicesClose({ data }) {
  const { indices, advances } = data

  return (
    <div className="card">
      <div className="card-label">INDIAN INDICES CLOSING</div>
      <table className="indices-table" style={{ width: '100%', borderCollapse: 'collapse', marginTop: 8 }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #000', textAlign: 'left' }}>
            <th style={{ padding: '6px 0', fontSize: '10px', fontWeight: '800', opacity: 0.6 }}>INDEX</th>
            <th style={{ padding: '6px 0', fontSize: '10px', fontWeight: '800', opacity: 0.6, textAlign: 'right' }}>CLOSE</th>
            <th style={{ padding: '6px 0', fontSize: '10px', fontWeight: '800', opacity: 0.6, textAlign: 'right' }}>CHG (%)</th>
          </tr>
        </thead>
        <tbody>
          {indices.map((idx) => (
            <tr key={idx.name} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '8px 0', fontSize: '12px', fontWeight: '700' }}>{idx.name}</td>
              <td style={{ padding: '8px 0', fontSize: '12px', fontWeight: '800', textAlign: 'right', fontFamily: 'JetBrains Mono' }}>
                {idx.close}
              </td>
              <td 
                style={{ 
                  padding: '8px 0', 
                  fontSize: '11px', 
                  fontWeight: '800', 
                  textAlign: 'right', 
                  fontFamily: 'JetBrains Mono',
                  color: idx.sign >= 0 ? '#16A34A' : '#DC2626'
                }}
              >
                {idx.pct}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="advances-bar" style={{ marginTop: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', fontWeight: '800', marginBottom: 4 }}>
          <span style={{ color: '#16A34A' }}>ADVANCES: {advances.adv}</span>
          <span style={{ color: '#DC2626' }}>DECLINES: {advances.dec}</span>
        </div>
        <div style={{ height: '6px', background: '#eee', borderRadius: '3px', display: 'flex', overflow: 'hidden', border: '1px solid #000' }}>
          <div style={{ width: `${(advances.adv / (advances.adv + advances.dec)) * 100}%`, background: '#16A34A' }} />
          <div style={{ flex: 1, background: '#DC2626' }} />
        </div>
      </div>
    </div>
  )
}
