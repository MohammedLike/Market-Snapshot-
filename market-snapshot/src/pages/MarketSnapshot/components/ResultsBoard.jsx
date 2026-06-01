import React from 'react'
import { motion } from 'framer-motion'

// revSign: 1 = green (positive filing), -1 = red (negative), 0 = neutral grey
const signStyle = (sign) => {
  if (sign > 0)  return { background: 'rgba(34,197,94,0.15)',  color: '#16A34A' }
  if (sign < 0)  return { background: 'rgba(239,68,68,0.15)',  color: '#DC2626' }
  return           { background: 'rgba(100,116,139,0.12)', color: '#64748B' }
}

export default function ResultsBoard({ data }) {
  const { results } = data

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="card-label">TODAY'S FILINGS</div>
      <table className="results-table">
        <tbody>
          {results.map((row, i) => (
            <tr key={`${row.company}-${i}`} className="results-row">
              {/* Company / symbol */}
              <td className="results-company">{row.company}</td>

              {/* Filing subject — colour-coded by sentiment */}
              <td>
                <span className="results-badge" style={signStyle(row.revSign)}>
                  {row.rev}
                </span>
              </td>

              {/* Time / source — always neutral */}
              <td>
                {row.np && (
                  <span className="results-badge" style={signStyle(0)}>
                    {row.np}
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  )
}
