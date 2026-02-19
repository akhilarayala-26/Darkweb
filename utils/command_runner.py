import subprocess
import sys


def execute_command(command: str, cwd: str = None):
    """
    Run a shell command, streaming stdout/stderr live.
    Raises RuntimeError if the subprocess exits with a non-zero code.
    """
    print(f"[cmd] Running: {command}" + (f"  (cwd={cwd})" if cwd else ""))

    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        text=True,
        # Stream directly to parent process stdout/stderr
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: {command}"
        )

    return {"status": "success", "return_code": 0}
