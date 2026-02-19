import subprocess
import time
import requests
import os
import platform
import shutil


def _find_tor_binary():
    """Auto-detect Tor binary location based on OS."""
    if platform.system() == "Windows":
        candidates = [
            r"C:\Users\AKHILA\OneDrive\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
            r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
            r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
            os.path.expanduser(r"~\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
    else:
        # macOS / Linux
        mac_path = "/opt/homebrew/bin/tor"
        if os.path.exists(mac_path):
            return mac_path

    # Fallback: search system PATH
    found = shutil.which("tor")
    return found or "tor"


def _popen_detach_kwargs():
    """Return OS-appropriate kwargs to detach a subprocess."""
    if platform.system() == "Windows":
        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    else:
        return {"start_new_session": True}


TOR_BINARY = _find_tor_binary()

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
        print("   Please install Tor and ensure it's in your PATH or at a standard location.")
        return False

    print("🧅 Starting Tor in background...")

    try:
        subprocess.Popen(
            [TOR_BINARY],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **_popen_detach_kwargs()
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
