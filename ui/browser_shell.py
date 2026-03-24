from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8088


def _port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _wait_for_http(url: str, timeout_s: float = 20.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.5) as response:
                if response.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.35)
    raise RuntimeError(f"UI bridge did not become ready within {timeout_s:.0f}s: {url}")


def _start_bridge(host: str, port: int) -> subprocess.Popen[str] | None:
    if _port_is_open(host, port):
        return None

    python_exe = os.environ.get("G4_DESKTOP_PYTHON") or sys.executable
    command = [python_exe, "-m", "ui.desktop.runtime_bridge", "--host", host, "--port", str(port)]
    return subprocess.Popen(command, cwd=str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the Geant4-Agent local web UI.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    bridge = _start_bridge(args.host, args.port)
    url = f"http://{args.host}:{args.port}"
    _wait_for_http(f"{url}/api/runtime")

    print(f"Geant4-Agent UI ready at {url}")
    if not args.no_browser:
        webbrowser.open(url)

    try:
        while True:
            time.sleep(1)
            if bridge and bridge.poll() is not None:
                raise RuntimeError("UI bridge exited unexpectedly.")
    except KeyboardInterrupt:
        pass
    finally:
        if bridge and bridge.poll() is None:
            bridge.terminate()
            try:
                bridge.wait(timeout=5)
            except Exception:
                bridge.kill()


if __name__ == "__main__":
    main()
