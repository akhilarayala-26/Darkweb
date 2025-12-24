import subprocess
import time
import requests
import os

TOR_BINARY = "/opt/homebrew/bin/tor"

TOR_PROXY = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}


def verify_tor_ip() -> bool:
    try:
        r = requests.get(
            "http://httpbin.org/ip",
            proxies=TOR_PROXY,
            timeout=10
        )
        return r.status_code == 200
    except Exception:
        return False


def start_tor() -> bool:
    if not os.path.exists(TOR_BINARY):
        print("❌ Tor binary not found at", TOR_BINARY)
        return False

    print("🧅 Starting Tor in background...")

    try:
        subprocess.Popen(
            [TOR_BINARY],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except Exception as e:
        print(f"❌ Failed to launch Tor: {e}")
        return False


def ensure_tor_running() -> bool:
    if verify_tor_ip():
        print("✅ Tor already running")
        return True

    if not start_tor():
        return False

    print("⏳ Waiting for Tor to bootstrap (this may take ~30s)...")
    time.sleep(30)

    if verify_tor_ip():
        print("✅ Tor started successfully")
        return True

    print("❌ Tor failed to bootstrap in time")
    return False
