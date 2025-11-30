# Portfolio Tracker for Car Thing

**Track your stock portfolio in real-time on your Car Thing display.**

**Created by Eli Gorelick** - [eligorelick.com](https://eligorelick.com)

---

## What This Does (Plain English)

This project turns your Spotify Car Thing into a real-time stock portfolio monitor. It shows:

- **Your stock holdings** with current prices, quantities, and values
- **Gains/losses** for each stock (both today's change and total since purchase)
- **Interactive chart** showing your portfolio value throughout the day (touch to scrub timeline)
- **Market status** indicator (open, closed, pre-market, after-hours)
- **Total portfolio value** including cash and money market funds

The display updates automatically every 10 minutes with fresh data from Yahoo Finance.

**Demo data is included!** You can try it immediately with sample stocks (AAPL, SPY, MSFT, VTI) before adding your own portfolio.

---

## Features

- Real-time stock prices via Yahoo Finance (uses reliable `regularMarketPrice` API)
- Holdings list with day/total gain (% and $)
- Interactive intraday chart with touch scrubbing
- Chart endpoint synced with holdings for accurate display
- Market status indicator (Open/Closed/Holiday/Weekend)
- Auto timezone detection for clock and chart
- Light/Dark theme toggle
- Auto-refresh every 10 minutes

## Files

```
portfolio-tracker/
├── START-SERVER.bat       <- Double-click to start server
├── DEPLOY.bat             <- Double-click to deploy + restart
├── portfolio_server.py    <- Server (edit your holdings here)
├── portfolio-display.html <- Display file
└── README.md
```

## Requirements

- Windows 10/11
- Python 3.7+ (python.org)
- Spotify Car Thing with Nocturne firmware
- USB data cable (not charge-only)

---

## Demo Portfolio Data

This project comes pre-loaded with sample data so you can see it in action immediately:

| Stock | Shares | Cost Basis | Description |
|-------|--------|------------|-------------|
| AAPL  | 3      | $120.00    | Apple Inc. |
| SPY   | 2      | $450.00    | S&P 500 ETF |
| MSFT  | 5      | $375.00    | Microsoft Corporation |
| VTI   | 10     | $220.00    | Total Stock Market ETF |
| Cash  | -      | $500.00    | Cash balance |
| Money Market | - | $2,500.00 | Money market funds |

**This is clearly marked as DEMO DATA in the code** and can be easily replaced with your actual holdings (see Step 3 below).

---

## Quick Start (Easiest Method)

**If this is your first time:**

1. Run `SETUP-WINDOWS.bat` in the main project folder
   - This wizard will guide you through everything automatically
2. Come back here and start at **Step 4** below

**If you've already set up the network:**

1. Skip to **Step 3** to configure your portfolio
2. Then continue with **Step 4** to run the server

---

## Setup Guide

### Step 1: Windows USB Network Setup

**Note:** You can skip this if you ran `SETUP-WINDOWS.bat` in the main folder.

1. **Connect Car Thing** via USB and wait for Windows to recognize it

2. **Find the network adapter name** - Open PowerShell and run:
   ```powershell
   Get-NetAdapter
   ```
   Look for "Ethernet 2", "Ethernet 3", or "Remote NDIS Compatible Device"

3. **Set static IP** (replace "Ethernet 3" with your adapter name):
   ```powershell
   netsh interface ip set address "Ethernet 3" static 172.16.42.1 255.255.255.0
   ```

4. **Enable Internet Sharing** (so Car Thing can sync time):
   - Open **Control Panel** > **Network and Sharing Center**
   - Click your main internet connection (WiFi or Ethernet)
   - Click **Properties** > **Sharing** tab
   - Check **"Allow other network users to connect"**
   - Select the Car Thing adapter from dropdown
   - Click **OK**

5. **Test connection**:
   ```powershell
   ping 172.16.42.2
   ```

### Step 2: Car Thing Setup

SSH into your Car Thing:
```bash
ssh root@172.16.42.2
# Password: nocturne
```

Run these commands:
```bash
mount -o remount,rw /
mkdir -p /opt/custom

# Configure chromium to load the portfolio display
sed -i 's|--app=http://localhost:80|--app=file:///opt/custom/portfolio-display.html|' /etc/sv/chromium/run
```

### Step 3: Configure Your Portfolio

**You can skip this step to use the DEMO DATA first and see how it works!**

When you're ready to track your real portfolio:

1. Right-click `portfolio_server.py` and open with Notepad (or your favorite text editor)
2. Find the section marked `CONFIGURE YOUR PORTFOLIO HERE` (around line 16)
3. Replace the HOLDINGS section with your actual stocks:

```python
HOLDINGS = {
    "AAPL": {"shares": 10, "cost_per_share": 150.00},  # Replace with your shares
    "MSFT": {"shares": 5, "cost_per_share": 300.00},   # Replace with your shares
    "GOOGL": {"shares": 8, "cost_per_share": 140.00},  # Add/remove stocks as needed
}

CASH = 1000.00           # Your cash balance
MONEY_MARKET = 5000.00   # Your money market balance (e.g., SWVXX)
```

**Important Notes:**
- Use the correct **stock ticker symbols** (e.g., "AAPL" not "Apple")
- `cost_per_share` is what you paid (your cost basis), not the current price
- Save the file when done
- Restart START-SERVER.bat to load your new portfolio

### Step 4: Start the Server

**Double-click `START-SERVER.bat`**

- Auto-installs yfinance if needed
- Runs on http://172.16.42.1:8080
- Keep this window open!

### Step 5: Deploy to Car Thing

**Double-click `DEPLOY.bat`**

This copies the HTML file and restarts chromium.

---

## Controls

| Control | Action |
|---------|--------|
| Button 1 | Holdings view |
| Button 2/3 | Chart view |
| Wheel (holdings) | Scroll list |
| Wheel (chart) | Scrub through time |
| Touch/drag chart | Scrub through time |
| Theme button | Light/dark toggle |

---

## Troubleshooting

### Can't ping 172.16.42.2

**Problem:** When you run `ping 172.16.42.2` it says "Request timed out"

**Solutions:**
1. Run the static IP command again (see Step 1)
2. Try a different USB port on your PC
3. Make sure Car Thing is powered on
4. Check that the USB cable supports data transfer (not charge-only)
5. Run `SETUP-WINDOWS.bat` in the main folder for automatic setup

### Server won't start

**Problem:** START-SERVER.bat shows "Python is not installed"

**Solutions:**
1. Install Python from [python.org/downloads](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart your computer
4. Run START-SERVER.bat again

### Can't deploy to Car Thing

**Problem:** DEPLOY.bat says "Could not connect to Car Thing"

**Solutions:**
1. Make sure Car Thing is connected via USB
2. Check that you can ping 172.16.42.2
3. Make sure you've run the Car Thing setup commands (Step 2)
4. Verify `/opt/custom/` folder exists on Car Thing

### No stock data showing

**Problem:** Portfolio shows but no prices or says "Loading..."

**Solutions:**
1. Wait 10-30 seconds for initial data fetch
2. Check your internet connection
3. Verify stock symbols are correct (e.g., "AAPL" not "Apple")
4. Look at the server window for error messages
5. Yahoo Finance might be slow - wait a few minutes

### Chart is empty or not updating

**Problem:** Chart view shows but no data points

**Solutions:**
1. This is normal outside market hours (Mon-Fri 9:30 AM - 4:00 PM ET)
2. Wait for market to open
3. Chart data only shows intraday (same day) data
4. Restart the server if you recently changed holdings

### Wrong time displayed on Car Thing

**Problem:** Clock shows incorrect time

**Solutions:**
1. Enable Internet Connection Sharing (see Step 1)
2. This allows Car Thing to sync time via NTP
3. Wait a few minutes for time sync to complete
4. The display auto-detects timezone from your holdings data

### Prices seem delayed or wrong

**Problem:** Prices don't match what you see on other sites

**Solutions:**
1. Prices update every 10 minutes (not real-time)
2. Yahoo Finance can have 15-minute delays
3. After-hours prices might differ from regular hours
4. Check the "Last Update" time on the display

### Want to track different stocks

**Problem:** Need to change the stocks being tracked

**Solution:**
1. Stop the server (close START-SERVER.bat window)
2. Edit `portfolio_server.py`
3. Update the HOLDINGS dictionary
4. Save the file
5. Run START-SERVER.bat again
6. Run DEPLOY.bat to refresh the display

---

## License

MIT
