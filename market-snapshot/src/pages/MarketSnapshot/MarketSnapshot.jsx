import React, { useRef, useState, useEffect } from 'react'
import { useSnapshot } from '../../hooks/useSnapshot'
import Header from './components/Header'
import MarketTicker from './components/MarketTicker'
import KeyLevels from './components/KeyLevels'
import GlobalCues from './components/GlobalCues'
import NiftyOutlook from './components/NiftyOutlook'
import BrentCrude from './components/BrentCrude'
import OptionsOI from './components/OptionsOI'
import SmartMoney from './components/SmartMoney'
import FIIDII from './components/FIIDII'
import ResultsBoard from './components/ResultsBoard'
import VolumeShockers from './components/VolumeShockers'
import SectorStrength from './components/SectorStrength'
import NewsBoard from './components/NewsBoard'
import IndicesClose from './components/IndicesClose'
import ADRGauge from './components/ADRGauge'
import SectorHeatmap from './components/SectorHeatmap'
import './MarketSnapshot.css'

export default function MarketSnapshot() {
  const { data, loading, error, lastUpdated, refetch } = useSnapshot()
  const gridRef = useRef(null)

  const [theme, setTheme] = useState(() => localStorage.getItem('market-theme') || 'light')
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('market-theme', theme)
  }, [theme])
  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light')

  async function handleExportPDF() {
    const { default: html2canvas } = await import('html2canvas')
    const { jsPDF } = await import('jspdf')
    const canvas = await html2canvas(gridRef.current, {
      backgroundColor: '#FFFFFF',
      scale: 2,
      useCORS: true,
    })
    const imgData = canvas.toDataURL('image/png')
    const pdf  = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pdfW = pdf.internal.pageSize.getWidth()
    const pdfH = (canvas.height * pdfW) / canvas.width
    pdf.addImage(imgData, 'PNG', 0, 0, pdfW, pdfH)
    pdf.save(`market-snapshot-${data.date.replace(/\s/g, '-')}.pdf`)
  }

  // ── Loading ───────────────────────────────────────────────
  if (loading && !data) {
    return (
      <div className="snapshot-page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="card-label" style={{ fontSize: 13, marginBottom: 12 }}>FETCHING LIVE MARKET DATA…</div>
          <div style={{ fontSize: 11, opacity: 0.5 }}>Connecting to market data sources</div>
        </div>
      </div>
    )
  }

  // ── Error (no data at all) ────────────────────────────────
  if (error && !data) {
    return (
      <div className="snapshot-page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <div className="card" style={{ maxWidth: 400, textAlign: 'center' }}>
          <div className="card-label" style={{ color: '#DC2626' }}>CONNECTION ERROR</div>
          <p className="card-body" style={{ margin: '8px 0' }}>
            Cannot reach the market data backend.<br />
            Make sure the FastAPI server is running:<br />
            <code style={{ fontSize: 11, background: '#F1F5F9', padding: '2px 6px', borderRadius: 3 }}>
              cd backend &amp;&amp; uvicorn main:app --port 8001 --reload
            </code>
          </p>
          <button className="export-btn" style={{ marginTop: 12 }} onClick={refetch}>Retry</button>
        </div>
      </div>
    )
  }

  // ── Main render ───────────────────────────────────────────
  return (
    <div className="snapshot-page">

      {/* Stale data banner */}
      {error && data && (
        <div style={{
          background: '#FEF3C7', borderBottom: '1px solid #F59E0B',
          padding: '6px 16px', fontSize: 11, fontWeight: 700,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <span>⚠ Live data refresh failed — showing last known data</span>
          <button onClick={refetch} style={{ background: 'none', border: '1px solid #F59E0B', borderRadius: 4, padding: '2px 8px', cursor: 'pointer', fontSize: 11 }}>
            Retry
          </button>
        </div>
      )}

      {/* ── Single page grid ── */}
      <div ref={gridRef} className="snapshot-grid">

        {/* Row 1: Header — full width */}
        <div className="full-width">
          <Header data={data} theme={theme} onToggleTheme={toggleTheme} />
        </div>

        {/* Row 2: Ticker — full width */}
        <div className="full-width">
          <MarketTicker data={data} />
        </div>

        {/* Row 3: Key Levels SVG — full width */}
        <div className="full-width">
          <KeyLevels data={data} />
        </div>

        {/* ── Row 4: first 3-column band ── */}

        {/* Col 1 */}
        <div className="col-stack">
          <GlobalCues data={data} />
          <NiftyOutlook data={data} />
          <BrentCrude data={data} />
        </div>

        {/* Col 2 */}
        <div className="col-stack">
          <OptionsOI data={data} />
          <SmartMoney data={data} />
          <FIIDII data={data} />
        </div>

        {/* Col 3 */}
        <div className="col-stack">
          <ResultsBoard data={data} />
          <div className="card">
            <VolumeShockers data={data} />
            <SectorStrength data={data} />
            <NewsBoard data={data} />
          </div>
        </div>

        {/* ── Row 5: second 3-column band (was page 2) ── */}

        {/* Col 1 */}
        <div className="col-stack">
          <IndicesClose data={data} />
        </div>

        {/* Col 2 */}
        <div className="col-stack">
          <ADRGauge data={data} />
          <SectorHeatmap data={data} />
        </div>

        {/* Col 3 */}
        <div className="col-stack">
          {data.technicalNote && (
            <div className="card" style={{ background: 'var(--bg-secondary)', borderStyle: 'dashed' }}>
              <div className="card-label">TECHNICAL NOTE</div>
              <p style={{ fontSize: '12px', lineHeight: '1.6', color: 'var(--text-main)', opacity: 0.8 }}>
                {data.technicalNote}
              </p>
            </div>
          )}
        </div>

      </div>

      {/* Footer / export bar */}
      <div className="export-bar">
        <button className="export-btn" onClick={handleExportPDF}>
          ⬇ Export PDF
        </button>
        <span className="footer-note">
          {lastUpdated
            ? `Live data as of ${lastUpdated.toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata' })} IST · ${data.date}`
            : `Report for ${data.date}`
          }. For educational purposes only.
        </span>
        <span className="footer-brand">Market DNA</span>
      </div>
    </div>
  )
}
