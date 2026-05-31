import React from 'react'
import { motion } from 'framer-motion'

export default function ResultsBoard({ data }) {
  const { results } = data

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <div className="card-label">Q4 RESULTS</div>
      <table className="results-table">
        <tbody>
          {results.map((row) => (
            <tr key={row.company} className="results-row">
              <td className="results-company">{row.company}</td>
              <td>
                <span
                  className="results-badge"
                  style={{
                    background: row.revSign >= 0 ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',
                    color: row.revSign >= 0 ? '#22C55E' : '#EF4444',
                  }}
                >
                  {row.rev}
                </span>
              </td>
              <td>
                <span
                  className="results-badge"
                  style={{
                    background: row.npSign >= 0 ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)',
                    color: row.npSign >= 0 ? '#22C55E' : '#EF4444',
                  }}
                >
                  {row.np}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </motion.div>
  )
}
