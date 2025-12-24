import subprocess

def ensure_warp_connected():
    result = subprocess.run(
        ["warp-cli", "status"],
        capture_output=True,
        text=True
    )

    if "Connected" not in result.stdout:
        subprocess.run(["warp-cli", "connect"], check=True)
