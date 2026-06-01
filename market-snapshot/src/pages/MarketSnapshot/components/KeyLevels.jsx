import React from 'react'

// ── SVG canvas constants ──────────────────────────────────────
const SVG_W   = 1000   // viewBox width
const PAD_L   = 10     // left padding inside viewBox
const PAD_R   = 10     // right padding inside viewBox
const TRACK_W = SVG_W - PAD_L - PAD_R   // usable track width

const TRACK_Y = 80     // top of the coloured bar
const TRACK_H = 32     // height of the coloured bar

// Label rows above the track (two alternating tiers)
const LABEL_Y_A = TRACK_Y - 42   // tier A  (odd levels)
const LABEL_Y_B = TRACK_Y - 22   // tier B  (even levels)

// Value rows below the track (two alternating tiers)
const VALUE_Y_A = TRACK_Y + TRACK_H + 18   // tier A
const VALUE_Y_B = TRACK_Y + TRACK_H + 34   // tier B

const SVG_H = VALUE_Y_B + 16   // total viewBox height

// Map a price value to an X pixel, clamped inside the track
function toX(value, min, max) {
  const raw = PAD_L + ((value - min) / (max - min)) * TRACK_W
  return Math.max(PAD_L, Math.min(SVG_W - PAD_R, raw))
}

export default function KeyLevels({ data }) {
  const { keyLevels } = data
  const { title, min, max, levels, zones, currentPrice, sentiment, sentimentSub } = keyLevels

  const cpX = toX(currentPrice, min, max)

  // Sentiment box: keep it fully inside the SVG
  const BOX_W = 170
  const BOX_H = 26
  const boxX = Math.max(PAD_L, Math.min(SVG_W - PAD_R - BOX_W, cpX - BOX_W / 2))

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
          {/* ── Background track ── */}
          <rect
            x={PAD_L} y={TRACK_Y}
            width={TRACK_W} height={TRACK_H}
            rx={14} fill="#1E293B"
          />

          {/* ── Coloured zones ── */}
          {zones.map((z, i) => {
            const x1 = toX(z.from, min, max)
            const x2 = toX(z.to,   min, max)
            const w  = Math.max(0, x2 - x1)
            const isFirst = i === 0
            const isLast  = i === zones.length - 1
            return (
              <rect
                key={i}
                x={x1} y={TRACK_Y}
                width={w} height={TRACK_H}
                fill={z.color}
                rx={isFirst || isLast ? 14 : 0}
              />
            )
          })}

          {/* ── Level lines + staggered labels ── */}
          {levels.map((lv, i) => {
            const x    = toX(lv.value, min, max)
            const isA  = i % 2 === 0          // alternating tier
            const lblY = isA ? LABEL_Y_A : LABEL_Y_B
            const valY = isA ? VALUE_Y_A : VALUE_Y_B

            return (
              <g key={i}>
                {/* Dashed vertical line spanning label → value */}
                <line
                  x1={x} y1={lblY + 4}
                  x2={x} y2={valY - 4}
                  stroke={lv.color}
                  strokeWidth={1}
                  strokeDasharray="3 2"
                  opacity={0.55}
                />
                {/* Label above track */}
                <text
                  x={x} y={lblY}
                  textAnchor="middle"
                  fontSize={9}
                  fontWeight={800}
                  fill={lv.color}
                  fontFamily="Inter, sans-serif"
                  letterSpacing={0.4}
                >
                  {lv.label}
                </text>
                {/* Numeric value below track */}
                <text
                  x={x} y={valY}
                  textAnchor="middle"
                  fontSize={10}
                  fontWeight={700}
                  fill="#64748B"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {lv.value.toLocaleString()}
                </text>
              </g>
            )
          })}

          {/* ── Current price marker ── */}
          {/* Vertical line through the full track */}
          <line
            x1={cpX} y1={TRACK_Y - 6}
            x2={cpX} y2={TRACK_Y + TRACK_H + 6}
            stroke="#EF4444"
            strokeWidth={2}
          />

          {/* Sentiment pill — clamped so it never overflows */}
          <rect
            x={boxX} y={TRACK_Y + (TRACK_H - BOX_H) / 2}
            width={BOX_W} height={BOX_H}
            rx={13}
            fill="#0F172A"
            stroke="#EF4444"
            strokeWidth={1.5}
          />
          <text
            x={boxX + BOX_W / 2}
            y={TRACK_Y + (TRACK_H - BOX_H) / 2 + 11}
            textAnchor="middle"
            fontSize={9.5}
            fontWeight={800}
            fill="#EF4444"
            fontFamily="Inter, sans-serif"
            letterSpacing={0.3}
          >
            {sentiment}
          </text>
          <text
            x={boxX + BOX_W / 2}
            y={TRACK_Y + (TRACK_H - BOX_H) / 2 + 21}
            textAnchor="middle"
            fontSize={7.5}
            fill="#94A3B8"
            fontFamily="Inter, sans-serif"
            fontWeight={600}
          >
            CMP: {currentPrice.toLocaleString()} • {sentimentSub}
          </text>
        </svg>
      </div>
    </div>
  )
}
