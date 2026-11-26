"""Launcher UI untuk exe PyInstaller — server + auto-buka browser.

Dipakai sebagai entry point build .exe: user awam cukup double-click,
tanpa perlu tahu port atau localhost. Port dipilih bebas agar tidak
bentrok dengan server lain.
"""

import socket
import threading
import webbrowser

import uvicorn

from beberes.ui.app import buat_app


def port_bebas() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> None:
    port = port_bebas()
    url = f"http://localhost:{port}"
    print(f"beberes UI -> {url}")
    print("Tutup jendela ini untuk menghentikan server.")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(buat_app(), host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
