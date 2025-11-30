# Car Thing Combined Dashboard

**All-in-one dashboard with Claude usage monitoring, stock portfolio tracking, and 2048 game.**

**Created by Eli Gorelick** - [eligorelick.com](https://eligorelick.com)

---

## What This Does (Plain English)

This is the **ultimate Car Thing dashboard** that combines three features into one display:

1. **Claude Usage Monitor (Tab 1)** - Track your Claude.ai API usage limits in real-time
   - Shows 5-hour, 7-day, and Sonnet-specific usage
   - Color-coded warnings when approaching limits
   - Auto-updates every 10 minutes

2. **Stock Portfolio Tracker (Tabs 2 & 3)** - Monitor your investments
   - Tab 2: Holdings list with prices and gains/losses
   - Tab 3: Interactive chart you can scrub through
   - Comes with **DEMO DATA** so you can try it immediately

3. **2048 Game (Tab 4)** - Entertainment when parked
   - Full implementation with score tracking
   - Use Car Thing buttons as arrow keys

Switch between features using the Car Thing's four buttons. Dark/light theme toggle included.

---

## Demo Portfolio Data Included

The portfolio tracker comes pre-loaded with sample data:

| Stock | Shares | Cost Basis |
|-------|--------|------------|
| AAPL  | 3      | $120.00    |
| SPY   | 2      | $450.00    |
| MSFT  | 5      | $375.00    |
| VTI   | 10     | $220.00    |

**You can try the portfolio feature immediately with this demo data** before adding your real holdings!

---

## Features

### Claude Usage Tab
- Real-time display of Claude usage limits
- 5-hour, 7-day, and Sonnet-specific usage tracking
- Color-coded progress bars (green/yellow/red)

### Portfolio Tab
- Real-time stock prices via Yahoo Finance (uses reliable `regularMarketPrice` API)
- Holdings list with day/total gain (% and $)
- Interactive intraday chart with touch scrubbing
- Chart endpoint synced with holdings for accurate display
- Auto timezone detection for chart labels

### Bonus
- 2048 game (press button 4)
- Dark/Light theme toggle
- Live clock display
- Auto-updates every 10 minutes

## Files

```
claude-carthingand portfolio-final/
├── START-SERVER.bat       <- Double-click to start server
├── DEPLOY.bat             <- Double-click to deploy to Car Thing
├── carthing_server.py     <- Server (configure here)
├── combined-display.html  <- Display UI (auto-timezone)
└── README.md
```

## Requirements

- Windows 10/11
- Python 3.8+ (python.org)
- Claude.ai Pro/Team subscription (for usage tracking)
- Spotify Car Thing with Nocturne firmware
- USB data cable (not charge-only)

---

## Quick Start (Easiest Method)

**First time setup:**

1. Run `SETUP-WINDOWS.bat` in the **main project folder** (one level up)
   - This wizard handles Python, OpenSSH, and network setup automatically
2. Return here to configure your Claude credentials (Step 1 below)
3. Start the server (Step 4 below)

**Already set up the network:**

1. Configure Claude credentials (Step 1)
2. Optionally configure your portfolio or use DEMO DATA (Step 2)
3. Start the server (Step 4)

---

## Detailed Setup Guide

### Step 1: Get Your Claude Credentials

**Required for Claude usage monitoring. Portfolio works with DEMO DATA without this.**

**ORG_ID:**
1. Go to [claude.ai](https://claude.ai) and log in
2. Press `F12` to open Developer Tools > **Network** tab
3. Look for any request URL containing `/organizations/`
4. Copy the ID (e.g., `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

**SESSION_KEY:**
1. In Developer Tools > **Application** tab > **Cookies**
2. Click on `https://claude.ai`
3. Find `sessionKey` and copy the value (starts with `sk-ant-sid01-`)

### Step 2: Configure the Server

Right-click `carthing_server.py` and open with Notepad (or your favorite editor).

**Claude Credentials (lines 34-35) - REQUIRED for Claude tab:**
```python
ORG_ID = "your-org-id-here"           # Replace with your org ID from Step 1
SESSION_KEY = "sk-ant-sid01-your-key" # Replace with your session key from Step 1
```

**Portfolio Holdings (line 48+) - OPTIONAL, DEMO DATA included:**
```python
# NOTE: DEMO DATA is already loaded - you can skip this and try it first!
HOLDINGS = {
    "AAPL": {"shares": 3, "cost_per_share": 120.00},  # Demo data
    "SPY": {"shares": 2, "cost_per_share": 450.00},   # Demo data
    "MSFT": {"shares": 5, "cost_per_share": 375.00},  # Demo data
    "VTI": {"shares": 10, "cost_per_share": 220.00},  # Demo data
}

CASH = 500.00            # Demo data
MONEY_MARKET = 2500.00   # Demo data
```

**To use your real portfolio:** Replace the holdings above with your actual stocks, cash, and money market balances. Use correct ticker symbols (e.g., "AAPL" not "Apple") and your cost basis (what you paid, not current price).

**Save the file** when done editing.

### Step 3: Windows USB Network Setup

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

### Step 4: Car Thing Setup

SSH into your Car Thing:
```bash
ssh root@172.16.42.2
# Password: nocturne
```

Run these commands:
```bash
mount -o remount,rw /
mkdir -p /opt/custom

# Configure chromium to load the combined display
sed -i 's|--app=http://localhost:80|--app=file:///opt/custom/combined-display.html|' /etc/sv/chromium/run
```

### Step 5: Start the Server

**Double-click `START-SERVER.bat`**

- Auto-installs Flask, curl_cffi, and yfinance if needed
- Runs on http://172.16.42.1:8080
- Keep this window open!

### Step 6: Deploy to Car Thing

**Double-click `DEPLOY.bat`**

This copies the HTML file and restarts chromium.

---

## Controls

| Control | Action |
|---------|--------|
| Button 1 | Claude usage view |
| Button 2 | Portfolio holdings |
| Button 3 | Portfolio chart |
| Button 4 | 2048 game |
| Wheel (holdings) | Scroll list |
| Touch/drag chart | Scrub through time |
| Arrow keys (game) | Move tiles |
| Theme button | Light/dark toggle |

---

## Troubleshooting

**Can't ping 172.16.42.2:** Re-run the static IP command, try different USB port

**Session Expired:** Get new SESSION_KEY from browser cookies

**Can't deploy:** Make sure Car Thing is connected and pingable

**Wrong time on Car Thing:** Internet sharing enables NTP time sync

**No portfolio data:** Wait 30 seconds for initial Yahoo Finance fetch

---

## License

MIT
