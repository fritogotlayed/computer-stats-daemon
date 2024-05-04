from __future__ import annotations

import logging

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from computer_stats_daemon.presentation.utils import setup_logging

PORT = 8889

async_mode = None
app = Flask(__name__, template_folder=".")
socket_ = SocketIO(app, async_mode=async_mode)


# log = logging.getLogger("werkzeug")
# log.setLevel(logging.ERROR)


# https://medium.com/swlh/implement-a-websocket-using-flask-and-socket-io-python-76afa5bbeae1


@app.route("/")
def index() -> str:
    """Render the index page."""
    return render_template("index.html", async_mode=socket_.async_mode)


@socket_.on("stats_update")
def stats_update(message: any) -> None:
    """Emit the stats update."""
    logging.debug("Received message: %s", message)
    emit("stats_update", message, broadcast=True)


def start_dashboard(log_level: int | str = logging.INFO, interactive: bool = False) -> None:
    """Start the dashboard."""
    setup_logging(log_level)
    socket_.run(app, debug=interactive, port=PORT, allow_unsafe_werkzeug=True)


def cli_entrypoint() -> None:
    """CLI entrypoint."""
    start_dashboard(logging.INFO)


if __name__ == "__main__":
    start_dashboard(logging.DEBUG)
