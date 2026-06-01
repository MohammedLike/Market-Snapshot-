/**
 * useSnapshot — fetches live market data from the FastAPI backend.
 *
 * During development the backend runs at http://localhost:8000.
 * In production set VITE_API_URL in your .env file.
 *
 * Falls back to the last known good data if a refresh fails,
 * so the UI never goes blank.
 */
import { useState, useEffect, useRef, useCallback } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'
const ENDPOINT = `${API_URL}/api/snapshot`

// Refresh interval in ms (60s during market hours, 5 min otherwise)
function getRefreshInterval() {
  const now = new Date()
  // Convert to IST (UTC+5:30)
  const istOffset = 5.5 * 60 * 60 * 1000
  const ist = new Date(now.getTime() + istOffset - now.getTimezoneOffset() * 60000)
  const h = ist.getHours()
  const m = ist.getMinutes()
  const totalMin = h * 60 + m
  if (totalMin >= 9 * 60 && totalMin <= 15 * 60 + 45) {
    return 60_000        // market hours: 60s
  }
  return 5 * 60_000      // off-hours: 5 min
}

export function useSnapshot() {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const timerRef = useRef(null)

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(ENDPOINT, { cache: 'no-store' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      setData(json)
      setError(null)
      setLastUpdated(new Date())
    } catch (err) {
      console.warn('[useSnapshot] fetch failed:', err.message)
      setError(err.message)
      // Keep stale data — don't clear it
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()

    function schedule() {
      const interval = getRefreshInterval()
      timerRef.current = setTimeout(() => {
        fetchData()
        schedule()
      }, interval)
    }
    schedule()

    return () => clearTimeout(timerRef.current)
  }, [fetchData])

  return { data, loading, error, lastUpdated, refetch: fetchData }
}
