from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import webview


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8088


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
    raise RuntimeError(f"Desktop bridge did not become ready within {timeout_s:.0f}s: {url}")


def _port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _start_bridge(host: str, port: int) -> subprocess.Popen[str] | None:
    if _port_is_open(host, port):
        return None

    python_exe = os.environ.get("G4_DESKTOP_PYTHON") or sys.executable
    command = [python_exe, "-m", "ui.desktop.runtime_bridge", "--host", host, "--port", str(port)]
    return subprocess.Popen(command, cwd=str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the Geant4-Agent desktop shell.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--title", default="Geant4-Agent Desktop")
    parser.add_argument("--width", type=int, default=1480)
    parser.add_argument("--height", type=int, default=980)
    args = parser.parse_args()

    bridge = _start_bridge(args.host, args.port)
    url = f"http://{args.host}:{args.port}"
    _wait_for_http(f"{url}/api/runtime")

    try:
        webview.create_window(
            title=args.title,
            url=url,
            width=args.width,
            height=args.height,
            min_size=(1100, 760),
            text_select=True,
        )
        webview.start(debug=False, gui="edgechromium")
    finally:
        if bridge and bridge.poll() is None:
            bridge.terminate()
            try:
                bridge.wait(timeout=5)
            except Exception:
                bridge.kill()


if __name__ == "__main__":
    main()
