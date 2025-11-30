#!/usr/bin/env python3
"""
Portfolio Tracker Server
Fetches real-time stock data from Yahoo Finance and serves JSON to the display.

Configure your holdings in the HOLDINGS dict below.
"""

import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import yfinance as yf

# =============================================================================
# CONFIGURE YOUR PORTFOLIO HERE
# =============================================================================

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

# Server configuration
SERVER_HOST = "172.16.42.1"  # Car Thing USB network interface
SERVER_PORT = 8080       # Port to serve on
UPDATE_INTERVAL = 600    # Update every 10 minutes (in seconds)

# =============================================================================

# Cache for fetched data
cache = {
    "holdings": None,
    "chart_data": None,
    "last_update": None
}


def fetch_portfolio_data():
    """Fetch current prices and day chart data from Yahoo Finance"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Fetching portfolio data...")

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
                    print(f"Warning: Missing price data for {symbol}, trying fast_info fallback")
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
                print(f"Error fetching {symbol}: {e}")

        # Sort by market value descending
        holdings_data.sort(key=lambda x: x["market_value"], reverse=True)

        # Add cash and money market
        total_market_value += CASH + MONEY_MARKET

        # Calculate portfolio day gain percent
        portfolio_previous = total_market_value - total_day_gain
        portfolio_day_gain_percent = (total_day_gain / portfolio_previous) * 100 if portfolio_previous > 0 else 0

        # Fetch intraday chart data - pass price_data for consistency
        chart_data = fetch_intraday_chart(symbols, price_data)

        cache["holdings"] = {
            "positions": holdings_data,
            "cash": CASH,
            "money_market": MONEY_MARKET,
            "total_market_value": round(total_market_value, 2),
            "total_cost": round(total_cost, 2),
            "total_day_gain_dollars": round(total_day_gain, 2),
            "total_day_gain_percent": round(portfolio_day_gain_percent, 2),
            "last_update": datetime.now().strftime("%H:%M:%S")
        }

        cache["chart_data"] = chart_data
        cache["last_update"] = datetime.now()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] Portfolio value: ${total_market_value:,.2f} | Day: {'+' if total_day_gain >= 0 else ''}${total_day_gain:,.2f}")

    except Exception as e:
        print(f"Error fetching data: {e}")


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
            # Get 1-day data with 5-minute intervals
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

        # Convert to sorted list
        chart_list = sorted(chart_points.values(), key=lambda x: x["time"])

        # Calculate previous close value for day gain - use passed price_data for consistency
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

            # Update the last point or add a new "now" point
            now_time = datetime.now().strftime("%H:%M")
            chart_list[-1]["value"] = current_value
            chart_list[-1]["components"] = components
            chart_list[-1]["time"] = now_time

        return {
            "points": chart_list,
            "previous_close": round(previous_close_value, 2)
        }

    except Exception as e:
        print(f"Error fetching chart data: {e}")
        return {"points": [], "previous_close": 0}


def update_loop():
    """Background thread to update data periodically"""
    while True:
        fetch_portfolio_data()
        time.sleep(UPDATE_INTERVAL)


class PortfolioHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Enable CORS
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if self.path == "/" or self.path == "/portfolio":
            data = cache["holdings"] or {"error": "Data not loaded yet"}
        elif self.path == "/chart":
            data = cache["chart_data"] or {"error": "Data not loaded yet"}
        elif self.path == "/health":
            data = {
                "status": "ok",
                "last_update": cache["last_update"].isoformat() if cache["last_update"] else None
            }
        elif self.path == "/all":
            data = {
                "holdings": cache["holdings"],
                "chart": cache["chart_data"],
                "last_update": cache["last_update"].isoformat() if cache["last_update"] else None
            }
        else:
            data = {
                "error": "Unknown endpoint",
                "endpoints": ["/", "/portfolio", "/chart", "/all", "/health"]
            }

        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass  # Suppress default logging


def main():
    print("=" * 50)
    print("Portfolio Tracker Server")
    print("=" * 50)
    print(f"Tracking {len(HOLDINGS)} positions")
    print(f"Update interval: {UPDATE_INTERVAL} seconds")
    print()

    # Start background update thread
    update_thread = threading.Thread(target=update_loop, daemon=True)
    update_thread.start()

    # Wait for initial data
    print("Fetching initial data...")
    while cache["holdings"] is None:
        time.sleep(1)

    # Start HTTP server
    server = HTTPServer((SERVER_HOST, SERVER_PORT), PortfolioHandler)
    print()
    print(f"Server running on http://{SERVER_HOST}:{SERVER_PORT}")
    print("Endpoints:")
    print("  /          - Portfolio holdings")
    print("  /portfolio - Portfolio holdings")
    print("  /chart     - Intraday chart data")
    print("  /all       - All data combined")
    print("  /health    - Server health check")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
