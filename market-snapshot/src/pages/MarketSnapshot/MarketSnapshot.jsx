import React, { useRef } from 'react'
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
import './MarketSnapshot.css'

export default function MarketSnapshot() {
  const { data, loading, error, lastUpdated, refetch } = useSnapshot()
  const reportRef = useRef(null)

  async function handleExportPDF() {
    const { default: html2canvas } = await import('html2canvas')
    const { jsPDF } = await import('jspdf')

    const pdf   = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pages = reportRef.current.querySelectorAll('.report-page')

    for (let i = 0; i < pages.length; i++) {
      const canvas = await html2canvas(pages[i], {
        backgroundColor: '#FFFFFF',
        scale: 2,
        useCORS: true,
      })
      const imgData = canvas.toDataURL('image/png')
      const pdfW   = pdf.internal.pageSize.getWidth()
      const pdfH   = (canvas.height * pdfW) / canvas.width
      if (i > 0) pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, 0, pdfW, pdfH)
    }

    pdf.save(`market-snapshot-${data.date.replace(/\s/g, '-')}.pdf`)
  }

  // ── Loading state ─────────────────────────────────────────
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

  // ── Error state (no data at all) ──────────────────────────
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
          <button className="export-btn" style={{ marginTop: 12 }} onClick={refetch}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  // ── Render (with stale-data banner if error) ──────────────
  return (
    <div className="snapshot-page">
      {/* Stale data warning banner */}
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

      <div ref={reportRef} className="report-container">

        {/* ── PAGE 1: EXECUTIVE SUMMARY ── */}
        <section className="report-page">
          <div className="page-header-mini">
            <span className="page-title-mini">MARKET SNAPSHOT · EXECUTIVE SUMMARY</span>
            <span className="page-num">PAGE 01</span>
          </div>

          <div className="snapshot-grid">
            <div className="full-width">
              <Header data={data} />
            </div>

            <div className="full-width">
              <MarketTicker data={data} />
            </div>

            <div className="full-width">
              <KeyLevels data={data} />
            </div>

            {/* Column 1 */}
            <div className="col-stack">
              <IndicesClose data={data} />
              <BrentCrude data={data} />
            </div>

            {/* Column 2 */}
            <div className="col-stack">
              <NiftyOutlook data={data} />
              <GlobalCues data={data} />
            </div>

            {/* Column 3 */}
            <div className="col-stack">
              <OptionsOI data={data} />
              <div className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
                <div>
                  <div className="card-label">MARKET SENTIMENT</div>
                  <div style={{
                    fontSize: '32px', fontWeight: '900',
                    color: data.sentiment?.color || '#DC2626',
                  }}>
                    {data.sentiment?.label || 'NEUTRAL'}
                  </div>
                  <div style={{ fontSize: '11px', fontWeight: '700', opacity: 0.6, marginTop: 4 }}>
                    Confidence: {data.sentiment?.confidence || 0}%
                  </div>
                  <div style={{ fontSize: '10px', opacity: 0.5, marginTop: 2 }}>
                    VOLUME-WEIGHTED ANALYSIS
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── PAGE 2: DEEP DIVE & DATA ── */}
        <section className="report-page">
          <div className="page-header-mini">
            <span className="page-title-mini">MARKET SNAPSHOT · DATA DEEP DIVE</span>
            <span className="page-num">PAGE 02</span>
          </div>

          <div className="snapshot-grid">
            {/* Column 1 */}
            <div className="col-stack">
              <SmartMoney data={data} />
              <FIIDII data={data} />
              <SectorStrength data={data} />
            </div>

            {/* Column 2 */}
            <div className="col-stack">
              <ResultsBoard data={data} />
            </div>

            {/* Column 3 */}
            <div className="col-stack">
              <VolumeShockers data={data} />
              <NewsBoard data={data} />
              {data.technicalNote && (
                <div className="card" style={{ flex: 1, background: '#F8FAFC', borderStyle: 'dashed' }}>
                  <div className="card-label">TECHNICAL NOTE</div>
                  <p style={{ fontSize: '11px', lineHeight: '1.5', color: '#475569' }}>
                    {data.technicalNote}
                  </p>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>

      {/* Export + footer */}
      <div className="export-bar">
        <button className="export-btn" onClick={handleExportPDF}>
          ⬇ Export 2-Page PDF
        </button>
        <span className="footer-note">
          {lastUpdated
            ? `Live data as of ${lastUpdated.toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata' })} IST · ${data.date}`
            : `After-market closing report for ${data.date}`
          }. For educational purposes only.
        </span>
        <span className="footer-brand">Market DNA</span>
      </div>
    </div>
  )
}
