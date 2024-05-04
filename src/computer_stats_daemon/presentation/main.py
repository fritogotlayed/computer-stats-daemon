from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys

import socketio
from socketio.exceptions import SocketIOError

from computer_stats_daemon.infrastructure.system import (
    get_collector_daemon_pid,
    get_dashboard_daemon_pid,
    is_pid_running,
    stop_collector_daemon,
    stop_dashboard_daemon,
    write_collector_daemon_pid,
    write_dashboard_daemon_pid,
)
from computer_stats_daemon.presentation.collector import start_collector
from computer_stats_daemon.presentation.dashboard import start_dashboard
from computer_stats_daemon.presentation.utils import setup_logging

SLEEP_SECONDS = 1


class Service(str):
    """Enum for the different services."""

    __slots__ = ()

    COLLECTOR = "collector"
    DASHBOARD = "dashboard"
    STATUS = "status"


def setup_cli_parser() -> argparse.ArgumentParser:
    """Set up the CLI parser."""
    parser = argparse.ArgumentParser(description="Computer stats daemon")
    parser.add_argument(
        "service", help="The service to run", choices=[Service.COLLECTOR, Service.DASHBOARD, Service.STATUS]
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--stop", action="store_true", help="Stop the daemon")
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


def cli_start_daemon(service: str) -> None:
    """Start the daemon."""
    setup_logging(logging.INFO)
    logging.info("Starting daemon...")
    daemon_pid = get_collector_daemon_pid() if service == Service.COLLECTOR else get_dashboard_daemon_pid()
    if daemon_pid != "" and is_pid_running(int(daemon_pid)):
        logging.error("Daemon is already running")
        sys.exit(1)
    command = "computer-stats-daemon" if service == Service.COLLECTOR else "computer-stats-dashboard"
    handle = subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # handle = subprocess.Popen([command])
    logging.info("Daemon started with PID %s", handle.pid)
    if service == Service.COLLECTOR:
        write_collector_daemon_pid(handle.pid)
    else:
        write_dashboard_daemon_pid(handle.pid)


def cli_stop_daemon(service: str) -> None:
    """Stop the daemon."""
    stop_code = stop_collector_daemon() if service == Service.COLLECTOR else stop_dashboard_daemon()
    if stop_code == 0:
        logging.info("Daemon stopped")
    else:
        logging.error("Daemon is not running")


def display_status() -> None:
    """Display the status of the daemons."""
    collector_pid = get_collector_daemon_pid()
    dashboard_pid = get_dashboard_daemon_pid()
    if collector_pid != "":
        logging.info("Collector daemon is running with PID %s", collector_pid)
    else:
        logging.info("Collector daemon is not running")
    if dashboard_pid != "":
        logging.info("Dashboard daemon is running with PID %s", dashboard_pid)
    else:
        logging.info("Dashboard daemon is not running")


def cli_entrypoint() -> None:
    """CLI entrypoint."""
    parser = setup_cli_parser()
    args = parser.parse_args()

    setup_logging(logging.INFO if not args.debug else logging.DEBUG)

    if args.service == Service.STATUS:
        display_status()
    elif args.service == Service.COLLECTOR:
        if args.interactive:
            start_collector(debug=args.debug)
        elif args.stop:
            cli_stop_daemon(Service.COLLECTOR)
        else:
            cli_start_daemon(Service.COLLECTOR)
    elif args.service == Service.DASHBOARD:
        if args.interactive:
            start_dashboard(logging.DEBUG if args.debug else logging.INFO, interactive=True)
        elif args.stop:
            cli_stop_daemon(Service.DASHBOARD)
        else:
            cli_start_daemon(Service.DASHBOARD)
