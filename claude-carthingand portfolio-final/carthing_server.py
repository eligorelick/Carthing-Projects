"""
Car Thing Dashboard Server
Combines Claude Usage + Portfolio Tracker into a single server

Created by Eli Gorelick - eligorelick.com
"""

from flask import Flask, jsonify
from curl_cffi import requests as curl_requests
import threading
import time
from datetime import datetime
import yfinance as yf

app = Flask(__name__)

# ============================================================
#                    CLAUDE CONFIGURATION
# ============================================================
#
# ORG_ID: Your Claude organization ID
#   1. Go to https://claude.ai/settings
#   2. Open DevTools (F12) -> Network tab
#   3. Look at any API request URL, it contains your org ID
#   4. Example: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
#
# SESSION_KEY: Your Claude session cookie
#   1. Go to https://claude.ai (make sure you're logged in)
#   2. Open DevTools (F12) -> Application tab -> Cookies
#   3. Click on https://claude.ai
#   4. Find "sessionKey" and copy its entire value
#   5. Example: sk-ant-sid01-xxxxx...
#
ORG_ID = "YOUR_ORG_ID_HERE"
SESSION_KEY = "YOUR_SESSION_KEY_HERE"
#
# ============================================================

# ============================================================
#                    PORTFOLIO CONFIGURATION
# ============================================================
# Add your stock holdings here
# Format: "SYMBOL": {"shares": NUMBER, "cost_per_share": PRICE}
#
# NOTE: The data below is SAMPLE/DEMO DATA for demonstration purposes.
# Replace with your actual holdings to track your real portfolio.
#
HOLDINGS = {
    "AAPL": {"shares": 3, "cost_per_share": 120.00},    # Demo: 3 shares @ $120
    "SPY": {"shares": 2, "cost_per_share": 450.00},     # Demo: 2 shares @ $450
    "MSFT": {"shares": 5, "cost_per_share": 375.00},    # Demo: 5 shares @ $375
    "VTI": {"shares": 10, "cost_per_share": 220.00},    # Demo: 10 shares @ $220
    # Add more stocks as needed...
}

CASH = 500.00            # Demo: Cash balance
MONEY_MARKET = 2500.00   # Demo: Money market balance (e.g., SWVXX at $1.00)
# ============================================================

# Fetch intervals (in seconds)
CLAUDE_FETCH_INTERVAL = 600   # 10 minutes
PORTFOLIO_FETCH_INTERVAL = 600  # 10 minutes

# Data caches
claude_data = {"status": "starting"}
portfolio_cache = {
    "holdings": None,
    "chart_data": None,
    "last_update": None
}


# ============================================================
#                    CLAUDE USAGE FUNCTIONS
# ============================================================

def fetch_claude_usage_loop():
    """Background thread that continuously fetches Claude usage data"""
    global claude_data

    print("\n" + "="*50)
    print("Starting Claude usage fetcher...")
    print("="*50 + "\n")

    while True:
        try:
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] Fetching Claude usage...")

            response = curl_requests.get(
                f"https://claude.ai/api/organizations/{ORG_ID}/usage",
                headers={
                    "Cookie": f"sessionKey={SESSION_KEY}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json",
                },
                impersonate="chrome"
            )

            if response.status_code == 200:
                claude_data = response.json()
                five_hour = claude_data.get('five_hour', {}).get('utilization', 'N/A')
                seven_day = claude_data.get('seven_day', {}).get('utilization', 'N/A')
                sonnet = claude_data.get('seven_day_sonnet', {}).get('utilization', 'N/A')
                print(f"[{timestamp}] Claude: 5-Hour: {five_hour}% | 7-Day: {seven_day}% | Sonnet: {sonnet}%")
            elif response.status_code == 401:
                print(f"[{timestamp}] Claude ERROR: Session expired")
                claude_data = {"error": "Session expired - update SESSION_KEY"}
            elif response.status_code == 403:
                print(f"[{timestamp}] Claude ERROR: Access denied")
                claude_data = {"error": "Access denied - check credentials"}
            else:
                print(f"[{timestamp}] Claude ERROR: HTTP {response.status_code}")
                claude_data = {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] Claude ERROR: {e}")
            claude_data = {"error": str(e)}

        time.sleep(CLAUDE_FETCH_INTERVAL)


# ============================================================
#                    PORTFOLIO FUNCTIONS
# ============================================================

def fetch_portfolio_data():
    """Fetch current prices and day chart data from Yahoo Finance"""
    global portfolio_cache

    timestamp = time.strftime('%H:%M:%S')
    print(f"[{timestamp}] Fetching portfolio data...")

    symbols = list(HOLDINGS.keys())
    holdings_data = []
    total_market_value = 0
    total_cost = 0
    total_day_gain = 0

    # Store price data for chart consistency
    price_data = {}

    try:
        # Fetch current data for all symbols using ticker.info (more reliable than fast_info)
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                # Use regularMarketPrice (reliable) instead of fast_info.last_price (unreliable)
                current_price = info.get('regularMarketPrice') or info.get('currentPrice')
                previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')

                if current_price is None or previous_close is None:
                    print(f"  Warning: Missing price data for {symbol}, trying fast_info fallback")
                    fast = ticker.fast_info
                    current_price = current_price or fast.last_price
                    previous_close = previous_close or fast.previous_close

                # Store for chart calculations
                price_data[symbol] = {
                    'current': current_price,
                    'previous_close': previous_close
                }

                shares = HOLDINGS[symbol]["shares"]
                cost_per_share = HOLDINGS[symbol]["cost_per_share"]

                market_value = current_price * shares
                total_cost_basis = cost_per_share * shares

                day_gain_dollars = (current_price - previous_close) * shares
                day_gain_percent = ((current_price - previous_close) / previous_close) * 100 if previous_close else 0

                total_gain_dollars = market_value - total_cost_basis
                total_gain_percent = ((market_value - total_cost_basis) / total_cost_basis) * 100 if total_cost_basis else 0

                holdings_data.append({
                    "symbol": symbol,
                    "shares": shares,
                    "current_price": round(current_price, 2),
                    "previous_close": round(previous_close, 2),
                    "cost_per_share": cost_per_share,
                    "market_value": round(market_value, 2),
                    "day_gain_dollars": round(day_gain_dollars, 2),
                    "day_gain_percent": round(day_gain_percent, 2),
                    "total_gain_dollars": round(total_gain_dollars, 2),
                    "total_gain_percent": round(total_gain_percent, 2),
                })

                print(f"  {symbol}: ${current_price:.2f} (prev: ${previous_close:.2f}, day: ${day_gain_dollars:+.2f})")

                total_market_value += market_value
                total_cost += total_cost_basis
                total_day_gain += day_gain_dollars

            except Exception as e:
                print(f"  Error fetching {symbol}: {e}")

        # Sort by market value descending
        holdings_data.sort(key=lambda x: x["market_value"], reverse=True)

        # Add cash and money market
        total_market_value += CASH + MONEY_MARKET

        # Calculate portfolio day gain percent
        portfolio_previous = total_market_value - total_day_gain
        portfolio_day_gain_percent = (total_day_gain / portfolio_previous) * 100 if portfolio_previous > 0 else 0

        # Fetch intraday chart data - pass price_data for consistency
        chart_data = fetch_intraday_chart(symbols, price_data)

        portfolio_cache["holdings"] = {
            "positions": holdings_data,
            "cash": CASH,
            "money_market": MONEY_MARKET,
            "total_market_value": round(total_market_value, 2),
            "total_cost": round(total_cost, 2),
            "total_day_gain_dollars": round(total_day_gain, 2),
            "total_day_gain_percent": round(portfolio_day_gain_percent, 2),
            "last_update": datetime.now().strftime("%H:%M:%S")
        }

        portfolio_cache["chart_data"] = chart_data
        portfolio_cache["last_update"] = datetime.now()

        print(f"[{timestamp}] Portfolio: ${total_market_value:,.2f} ({total_day_gain:+,.2f} today)")

    except Exception as e:
        print(f"[{timestamp}] Portfolio ERROR: {e}")


def fetch_intraday_chart(symbols, price_data=None):
    """Fetch intraday data and calculate portfolio value over time

    Args:
        symbols: List of stock symbols
        price_data: Dict of {symbol: {'current': price, 'previous_close': price}} for consistency
    """
    try:
        chart_points = {}

        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="5m")

            if hist.empty:
                continue

            shares = HOLDINGS[symbol]["shares"]

            for timestamp, row in hist.iterrows():
                ts_str = timestamp.strftime("%H:%M")
                if ts_str not in chart_points:
                    chart_points[ts_str] = {
                        "time": ts_str,
                        "timestamp": timestamp.isoformat(),
                        "value": CASH + MONEY_MARKET,
                        "components": {}
                    }
                chart_points[ts_str]["value"] += row["Close"] * shares
                chart_points[ts_str]["components"][symbol] = round(row["Close"] * shares, 2)

        chart_list = sorted(chart_points.values(), key=lambda x: x["time"])

        # Calculate previous close value - use passed price_data for consistency
        previous_close_value = CASH + MONEY_MARKET
        for symbol in symbols:
            if price_data and symbol in price_data:
                # Use the same previous_close as the holdings calculation
                previous_close_value += price_data[symbol]['previous_close'] * HOLDINGS[symbol]["shares"]
            else:
                # Fallback: fetch from ticker.info (reliable)
                ticker = yf.Ticker(symbol)
                info = ticker.info
                prev_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                if prev_close is None:
                    prev_close = ticker.fast_info.previous_close
                previous_close_value += prev_close * HOLDINGS[symbol]["shares"]

        # Add/update final point with actual current prices to match holdings calculation
        # This ensures the chart endpoint matches what's shown in the holdings view
        if price_data and chart_list:
            current_value = CASH + MONEY_MARKET
            components = {}
            for symbol in symbols:
                if symbol in price_data:
                    val = price_data[symbol]['current'] * HOLDINGS[symbol]["shares"]
                    current_value += val
                    components[symbol] = round(val, 2)

            # Update the last point with current prices
            now_time = datetime.now().strftime("%H:%M")
            chart_list[-1]["value"] = current_value
            chart_list[-1]["components"] = components
            chart_list[-1]["time"] = now_time

        return {
            "points": chart_list,
            "previous_close": round(previous_close_value, 2)
        }

    except Exception as e:
        print(f"  Chart ERROR: {e}")
        return {"points": [], "previous_close": 0}


def fetch_portfolio_loop():
    """Background thread to update portfolio data"""
    while True:
        fetch_portfolio_data()
        time.sleep(PORTFOLIO_FETCH_INTERVAL)


# ============================================================
#                    API ENDPOINTS
# ============================================================

@app.route('/')
def index():
    """Root endpoint - shows server status"""
    return jsonify({
        "status": "ok",
        "server": "Car Thing Dashboard Server",
        "endpoints": ["/claude", "/portfolio", "/chart"],
        "claude_data": "five_hour" in claude_data,
        "portfolio_data": portfolio_cache["holdings"] is not None
    })


@app.route('/claude')
@app.route('/usage')
def get_claude_usage():
    """Endpoint for Claude usage data"""
    response = jsonify(claude_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/portfolio')
@app.route('/holdings')
def get_portfolio():
    """Endpoint for portfolio holdings data"""
    data = portfolio_cache["holdings"] or {"error": "Data not loaded yet"}
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/chart')
def get_chart():
    """Endpoint for intraday chart data"""
    data = portfolio_cache["chart_data"] or {"error": "Data not loaded yet"}
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/all')
def get_all():
    """Endpoint for all portfolio data (holdings + chart)"""
    data = {
        "holdings": portfolio_cache["holdings"],
        "chart": portfolio_cache["chart_data"],
        "last_update": portfolio_cache["last_update"].isoformat() if portfolio_cache["last_update"] else None
    }
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "claude_data": "five_hour" in claude_data,
        "portfolio_data": portfolio_cache["holdings"] is not None
    })


# ============================================================
#                    MAIN
# ============================================================

def print_banner():
    """Print startup banner"""
    print("\n")
    print("  ╔═══════════════════════════════════════════════╗")
    print("  ║      Car Thing Dashboard Server               ║")
    print("  ║      Claude Usage + Portfolio Tracker         ║")
    print("  ║                                               ║")
    print("  ║      Created by Eli Gorelick                  ║")
    print("  ║      eligorelick.com                          ║")
    print("  ╚═══════════════════════════════════════════════╝")
    print("\n")


if __name__ == '__main__':
    print_banner()

    # Check if Claude credentials are configured
    if ORG_ID == "YOUR_ORG_ID_HERE" or SESSION_KEY == "YOUR_SESSION_KEY_HERE":
        print("  [!] WARNING: Claude credentials not configured!")
        print("      Edit this file and set ORG_ID and SESSION_KEY")
        print("")

    # Start background fetcher threads
    claude_thread = threading.Thread(target=fetch_claude_usage_loop, daemon=True)
    claude_thread.start()

    portfolio_thread = threading.Thread(target=fetch_portfolio_loop, daemon=True)
    portfolio_thread.start()

    print(f"  Server: http://172.16.42.1:8080")
    print(f"  Endpoints:")
    print(f"    /claude    - Claude usage data")
    print(f"    /portfolio - Portfolio holdings")
    print(f"    /chart     - Intraday chart data")
    print(f"    /all       - All portfolio data")
    print("")
    print("  Press Ctrl+C to stop")
    print("")
    print("-"*50)

    # Wait for initial data
    print("\nWaiting for initial data...")
    timeout = 60
    start = time.time()
    while portfolio_cache["holdings"] is None and (time.time() - start) < timeout:
        time.sleep(1)

    if portfolio_cache["holdings"] is None:
        print("Warning: Portfolio data still loading, starting server anyway...")

    print("\n" + "-"*50)
    print("Server starting...")
    print("-"*50 + "\n")

    # Start the Flask server
    app.run(host='172.16.42.1', port=8080, threaded=True)
