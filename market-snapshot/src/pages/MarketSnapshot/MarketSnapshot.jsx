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
  const data = useSnapshot()
  const reportRef = useRef(null)

  async function handleExportPDF() {
    const { default: html2canvas } = await import('html2canvas')
    const { jsPDF } = await import('jspdf')
    
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const pages = reportRef.current.querySelectorAll('.report-page')

    for (let i = 0; i < pages.length; i++) {
      const canvas = await html2canvas(pages[i], {
        backgroundColor: '#FFFFFF',
        scale: 2,
        useCORS: true,
      })
      const imgData = canvas.toDataURL('image/png')
      const pdfW = pdf.internal.pageSize.getWidth()
      const pdfH = (canvas.height * pdfW) / canvas.width
      
      if (i > 0) pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, 0, pdfW, pdfH)
    }

    pdf.save(`market-snapshot-${data.date.replace(/\s/g, '-')}.pdf`)
  }

  return (
    <div className="snapshot-page">
      <div ref={reportRef} className="report-container">
        
        {/* --- PAGE 1: EXECUTIVE SUMMARY --- */}
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
                  <div style={{ fontSize: '32px', fontWeight: '900', color: '#DC2626' }}>BEARISH</div>
                  <div style={{ fontSize: '10px', fontWeight: '700', opacity: 0.6 }}>VOLUME-WEIGHTED ANALYSIS</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* --- PAGE 2: DEEP DIVE & DATA --- */}
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
              <div className="card" style={{ flex: 1, background: '#F8FAFC', borderStyle: 'dashed' }}>
                <div className="card-label">TECHNICAL NOTE</div>
                <p style={{ fontSize: '11px', lineHeight: '1.5', color: '#475569' }}>
                  The late-session sell-off in heavyweights like Reliance and HDFC Bank suggests further weakness. 
                  Watch 23,800 as the ultimate support floor for the current expiry.
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Export button — outside grid so it doesn't appear in PDF */}
      <div className="export-bar">
        <button className="export-btn" onClick={handleExportPDF}>
          ⬇ Export 2-Page PDF
        </button>
        <span className="footer-note">
          After-market closing report for {data.date}. For educational purposes only.
        </span>
        <span className="footer-brand">Daily Insight</span>
      </div>
    </div>
  )
}
