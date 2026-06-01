# Market Snapshot — Professional Trading Dashboard

Market Snapshot is a high-performance, full-stack trading dashboard designed to provide a comprehensive "Outside-In" view of the Indian Equities market (NSE). It synthesizes macro cues, institutional positioning, and technical analytics into a single, professional-grade interface.

![Dashboard Preview](https://via.placeholder.com/1200x600?text=Market+Snapshot+Dashboard+Preview)

## 🚀 Key Features

### 1. Intelligence & Sentiment
*   **AI Market Mood**: A heuristic engine that analyzes institutional data, breadth, and volatility to generate a real-time market pulse summary.
*   **Dynamic Sentiment Gauge**: Volume-weighted analysis of market conditions (Bullish, Bearish, or Neutral).
*   **Global Opening Alignment**: Predictive confidence score for the market open based on overnight performance of Dow, Nasdaq, and FTSE.

### 2. Professional Market Metrics
*   **Market Breadth (ADR)**: Real-time Advances/Declines "thermometer" for the Nifty 500.
*   **Sector Heatmap**: Dynamic performance visualization across major sectors (IT, Banking, Auto, Energy, etc.).
*   **Technical DMA Scan**: Automated tracking of 50-day and 200-day Daily Moving Averages with Golden/Death Cross alerts.
*   **RSI (14) Monitoring**: Identification of Overbought (>70) and Oversold (<30) conditions across major indices.

### 3. Institutional "Pro" Data
*   **FII Index Long-Short Ratio**: Deep-dive into institutional futures positioning to identify trend reversals.
*   **High-Conviction Delivery**: Real-time NSE delivery percentage scanner to differentiate between "intraday gambling" and "long-term accumulation."
*   **FII/DII Cash Flow**: Daily buy/sell activity from institutional investors.

### 4. Macro & News
*   **Corporate Announcements**: Specific, stock-related news pulled directly from NSE/BSE corporate filings.
*   **Economic Calendar**: Tracking of high-impact global events (RBI Policy, US Fed Meetings, CPI Data).
*   **Brent Crude & USD/INR**: Real-time tracking of critical macro indicators.

---

## 🛠 Tech Stack & Architecture

### Frontend
*   **Framework**: React 18 + Vite
*   **Styling**: Dynamic CSS Variable System (Light/Dark Mode)
*   **Animations**: Framer Motion
*   **Charts**: Recharts & Custom SVG Visualizations
*   **Exports**: html2canvas + jsPDF for high-resolution PDF reporting.

### Backend
*   **Server**: FastAPI (Python 3.10+)
*   **Async Processing**: APScheduler for background data synchronization.
*   **Data Sources**: 
    *   **Yahoo Finance**: Price action, historical data, and global news.
    *   **NSE India**: Options Chain, FII/DII data, and Corporate Filings (via session-handshake).
*   **Caching**: In-memory snapshot caching with a 60s TTL during market hours.

### Architecture Overview
1.  **Fetcher Layer**: Asynchronous modules connect to public APIs (NSE, Yahoo).
2.  **Analytics Layer**: Raw data is processed for technical indicators (DMA, RSI), institutional ratios, and sentiment logic.
3.  **Snapshot Builder**: Orchestrates all data into a unified JSON payload matching the frontend schema.
4.  **API Layer**: Serves the snapshot via a RESTful endpoint with CORS protection.

---

## ⚡ Getting Started

### Prerequisites
*   Node.js (v18+)
*   Python (v3.10+)
*   pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MohammedLike/Market-Snapshot-.git
   cd Market-Snapshot-
   ```

2. **Install Dependencies:**
   ```bash
   # Install root and frontend packages
   npm install

   # Install backend packages
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

### Running the Dashboard
You can start both the Frontend and Backend with a single command from the root folder:
```bash
npm run dev
```

*   **Frontend**: [http://localhost:5200](http://localhost:5200)
*   **Backend**: [http://localhost:8001](http://localhost:8001)

---

## 🌙 Customization
*   **Dark Mode**: Toggle via the 🌙 icon in the top right. Preferences are persisted in `localStorage`.
*   **Watchlist**: (Upcoming) Personalized stock tracking integration.

## 📄 License
For educational purposes only. Market data is sourced from public APIs and may be delayed.

**Developed by Market DNA**
