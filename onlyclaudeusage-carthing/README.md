# Claude Usage Monitor for Car Thing

**Monitor your Claude.ai API usage limits in real-time on your Car Thing display.**

**Created by Eli Gorelick** - [eligorelick.com](https://eligorelick.com)

---

## What This Does (Plain English)

This project turns your Spotify Car Thing into a real-time Claude.ai usage monitor. It shows:

- **Your Claude usage** across 5-hour, 7-day, and Sonnet-specific limits
- **Color-coded progress bars** that turn yellow at 50%, red at 80%
- **Warning animations** when you're approaching limits
- **Live clock** with automatic timezone detection
- **Auto-refresh** every 10 minutes to stay up-to-date

Perfect for Claude Pro/Team users who want to monitor their usage without constantly checking the browser.

---

## Features

- Real-time display of Claude usage limits
- 5-hour, 7-day, and Sonnet-specific usage tracking
- Color-coded progress bars (green → yellow → red)
- Warning animation when usage exceeds 80%
- Dark/Light theme toggle
- Live clock display (auto timezone)
- Auto-updates every 10 minutes

## Files

```
onlyclaudeusage-carthing/
├── START-SERVER.bat          <- Double-click to start server
├── DEPLOY.bat                <- Double-click to deploy to Car Thing
├── claude_usage_server.py    <- Server (edit your credentials here)
├── claude-usage-display.html <- Display file
└── README.md
```

## Requirements

- Windows 10/11
- Python 3.8+ (python.org)
- Claude.ai Pro/Team subscription
- Spotify Car Thing with Nocturne firmware
- USB data cable (not charge-only)

---

## Setup Guide

### Step 1: Get Your Claude Credentials

**ORG_ID:**
1. Go to [claude.ai](https://claude.ai) and log in
2. Press `F12` to open Developer Tools > **Network** tab
3. Click on any chat or refresh the page
4. Look for any request URL containing `/organizations/`
5. Copy the ID (e.g., `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

**SESSION_KEY:**
1. In Developer Tools > **Application** tab > **Cookies**
2. Click on `https://claude.ai`
3. Find `sessionKey` and copy the value (starts with `sk-ant-sid01-`)

### Step 2: Configure the Server

Edit `claude_usage_server.py` and replace:
```python
ORG_ID = "YOUR_ORG_ID_HERE"
SESSION_KEY = "YOUR_SESSION_KEY_HERE"
```

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

# Configure chromium to load the Claude usage display
sed -i 's|--app=http://localhost:80|--app=file:///opt/custom/claude-usage-display.html|' /etc/sv/chromium/run
```

### Step 5: Start the Server

**Double-click `START-SERVER.bat`**

- Auto-installs Flask and curl_cffi if needed
- Runs on http://172.16.42.1:8080
- Keep this window open!

### Step 6: Deploy to Car Thing

**Double-click `DEPLOY.bat`**

This copies the HTML file and restarts chromium.

---

## Troubleshooting

### Can't ping 172.16.42.2

**Problem:** When you run `ping 172.16.42.2` it says "Request timed out"

**Solutions:**
1. Run the static IP command again (see Step 3)
2. Try a different USB port on your PC
3. Make sure Car Thing is powered on with Nocturne firmware
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
3. Make sure you've run the Car Thing setup commands (Step 4)
4. Verify `/opt/custom/` folder exists on Car Thing
5. Try running DEPLOY.bat again after restarting Car Thing

### Session expired or invalid credentials

**Problem:** Usage data shows "Error" or doesn't load

**Solutions:**
1. Get a fresh SESSION_KEY from browser (see Step 1)
2. Session keys expire - you'll need to update them periodically
3. Make sure ORG_ID is correct (doesn't change often)
4. Check the server window for specific error messages
5. Verify you have a Claude Pro or Team subscription

### No usage data showing

**Problem:** Display shows but all values are at 0% or "Loading..."

**Solutions:**
1. Wait 10-30 seconds for initial data fetch
2. Check your internet connection
3. Verify credentials are correctly entered in claude_usage_server.py
4. Look at the server window for error messages
5. Session key may have expired - get a new one

### Wrong time displayed on Car Thing

**Problem:** Clock shows incorrect time

**Solutions:**
1. Enable Internet Connection Sharing (see Step 3)
2. This allows Car Thing to sync time via NTP
3. Wait a few minutes for time sync to complete
4. Restart Car Thing if time still doesn't sync

### Usage percentages seem wrong

**Problem:** Numbers don't match what you see on claude.ai

**Solutions:**
1. Usage updates every 10 minutes (not real-time)
2. Check the "Last Update" time on the display
3. Refresh the browser on claude.ai to compare
4. Claude.ai API might have delays
5. Restart the server to force a fresh fetch

---

## Quick Start (Easiest Method)

**First time setup:**

1. Run `SETUP-WINDOWS.bat` in the **main project folder** (one level up)
   - This wizard handles Python, OpenSSH, and network setup automatically
2. Return here to configure your Claude credentials (Step 1 & 2)
3. Start the server (Step 5)

---

## License

MIT
