import data from '../data/marketSnapshot.json'

/**
 * useSnapshot — single source of truth for all Market Snapshot components.
 * Later: replace with async fetch() + useEffect for live data.
 * The component tree stays identical — only this hook changes.
 */
export const useSnapshot = () => data
