import React from 'react'

const SVG_W = 900
const SVG_H = 150
const TRACK_Y = 70
const TRACK_H = 28
const PAD_L = 50
const PAD_R = 50

function toX(value, min, max) {
  return PAD_L + ((value - min) / (max - min)) * (SVG_W - PAD_L - PAD_R)
}

export default function KeyLevels({ data }) {
  const { keyLevels } = data
  const { title, min, max, levels, zones, currentPrice, sentiment, sentimentSub } = keyLevels

  const cpX = toX(currentPrice, min, max)

  return (
    <div className="card key-levels-card">
      <div className="card-label">{title}</div>
      <div className="key-levels-svg-wrap">
        <svg
          viewBox={`0 0 ${SVG_W} ${SVG_H}`}
          preserveAspectRatio="xMidYMid meet"
          className="key-levels-svg"
          aria-label="Nifty 50 intraday key levels range bar"
        >
          {/* Background track */}
          <rect x={PAD_L} y={TRACK_Y} width={SVG_W - PAD_L - PAD_R} height={TRACK_H} rx={4} fill="#1E293B" />

          {/* Colored zones */}
          {zones.map((z, i) => {
            const x1 = toX(z.from, min, max)
            const x2 = toX(z.to, min, max)
            return (
              <rect key={i} x={x1} y={TRACK_Y} width={Math.max(0, x2 - x1)} height={TRACK_H} fill={z.color} />
            )
          })}

          {/* Level dashed lines */}
          {levels.map((lv, i) => {
            const x = toX(lv.value, min, max)
            const isEven = i % 2 === 0
            return (
              <g key={i}>
                <line
                  x1={x} y1={TRACK_Y - 30}
                  x2={x} y2={TRACK_Y + TRACK_H + 10}
                  stroke={lv.color}
                  strokeWidth={1.5}
                  strokeDasharray="4 3"
                />
                {/* Label above - staggered */}
                <text
                  x={x} y={isEven ? TRACK_Y - 35 : TRACK_Y - 52}
                  textAnchor="middle"
                  fontSize={10}
                  fontWeight={700}
                  fill={lv.color}
                  fontFamily="Plus Jakarta Sans, sans-serif"
                  letterSpacing={0.5}
                >
                  {lv.label}
                </text>
                {/* Value below - staggered */}
                <text
                  x={x} y={isEven ? TRACK_Y + TRACK_H + 22 : TRACK_Y + TRACK_H + 38}
                  textAnchor="middle"
                  fontSize={10}
                  fill="#64748B"
                  fontWeight={600}
                  fontFamily="JetBrains Mono, monospace"
                >
                  {lv.value}
                </text>
              </g>
            )
          })}

          {/* Current price indicator */}
          <g>
            {/* Price Marker Line */}
            <line 
              x1={cpX} y1={TRACK_Y - 5} 
              x2={cpX} y2={TRACK_Y + TRACK_H + 5} 
              stroke="#EF4444" 
              strokeWidth={3} 
            />
            
            {/* Sentiment box - opaque to cover lines behind it */}
            <rect 
              x={cpX - 75} y={TRACK_Y + 3} 
              width={150} height={22} 
              rx={4} fill="#0F172A" 
              stroke="#EF4444" 
              strokeWidth={1} 
            />
            <text 
              x={cpX} y={TRACK_Y + 13} 
              textAnchor="middle" fontSize={10} 
              fontWeight={800} fill="#EF4444" 
              fontFamily="Plus Jakarta Sans, sans-serif"
            >
              {sentiment.toUpperCase()}
            </text>
            <text 
              x={cpX} y={TRACK_Y + 21} 
              textAnchor="middle" fontSize={8} 
              fill="#94A3B8" fontFamily="Plus Jakarta Sans, sans-serif"
              fontWeight={600}
            >
              {sentimentSub}
            </text>
          </g>
        </svg>
      </div>
    </div>
  )
}
