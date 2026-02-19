import subprocess
import platform
import shutil
import os


def _find_warp_cli():
    """Auto-detect warp-cli binary location based on OS."""
    if platform.system() == "Windows":
        # Default WARP install location on Windows
        win_path = r"C:\Program Files\Cloudflare\Cloudflare WARP\warp-cli.exe"
        if os.path.exists(win_path):
            return win_path

    # Fallback: assume it's in PATH (works for macOS/Linux and Windows if PATH is set)
    found = shutil.which("warp-cli")
    return found or "warp-cli"


WARP_CLI = _find_warp_cli()


def ensure_warp_connected():
    result = subprocess.run(
        [WARP_CLI, "status"],
        capture_output=True,
        text=True
    )

    if "Connected" not in result.stdout:
        subprocess.run([WARP_CLI, "connect"], check=True)
