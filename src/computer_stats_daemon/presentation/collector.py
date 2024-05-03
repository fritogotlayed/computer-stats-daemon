import argparse
import json
import logging
import time

import socketio
from socketio.exceptions import SocketIOError

from computer_stats_daemon.core.logic import start_stats_emitter
from computer_stats_daemon.infrastructure.system import read_config
from computer_stats_daemon.presentation.utils import setup_logging


def setup_cli_parser() -> argparse.ArgumentParser:
    """Set up the CLI parser."""
    parser = argparse.ArgumentParser(description="Computer stats daemon")
    parser.add_argument("--no-emit", action="store_true", help="Do not emit stats to the dashboard")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser


def output_stats(stats: dict, sio: socketio.Client = None) -> None:
    """Output the stats."""
    for key, value in stats.items():
        logging.debug("%s usage: %s", key, value)

    if sio is not None and sio.connected:
        try:
            sio.emit("stats_update", json.dumps(stats))
        except SocketIOError:
            logging.exception("Error sending stats")


def get_config_value(config: dict, key: str, args: argparse.Namespace, kwargs: dict, default: str) -> str:
    """Get the configuration value."""
    if kwargs.get(key) is not None:
        return kwargs[key]
    if args.__dict__.get(key) is not None:
        return "true" if args.__dict__[key] else "false"
    return config["DEFAULT"][key] if config["DEFAULT"][key] else default


def start_collector(**kwargs: str) -> None:
    """Start the collector.

    Args:
        **kwargs: The keyword arguments. The following are supported: debug, display_host, sleep_seconds.
    """
    parser = setup_cli_parser()
    args = parser.parse_args()
    config = read_config()

    # The function is called from multiple places. As such the configuration values are processed in the following way:
    # 1. The configuration is read from the configuration file and will be overridden by further arguments.
    # 2. The argparse arguments are processed and override the configuration file.
    # 3. The function arguments are processed and override the argparse arguments.
    is_debug: bool = get_config_value(config, "debug", args, kwargs, "false") == "true"
    display_host: str = get_config_value(config, "display_host", args, kwargs, "http://localhost:8889")
    sleep_seconds: int = int(get_config_value(config, "sleep_seconds", args, kwargs, "1"))

    setup_logging(logging.DEBUG if is_debug else logging.INFO)

    sio = socketio.Client()
    if args.no_emit is False:
        while True:
            try:
                sio.connect(display_host)
                break
            except SocketIOError:
                if is_debug:
                    logging.exception("Failed to connect to the dashboard, retrying...")
                time.sleep(1)
                continue

    start_stats_emitter(
        int(sleep_seconds),
        lambda stats: output_stats(stats, sio if args.no_emit is False else None),
    )
