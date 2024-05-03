import configparser
import os
from pathlib import Path

CONFIG_FILE_NAME = "config.toml"
COLLECTOR_PID_FILE_NAME = "collector.pid"
DASHBOARD_PID_FILE_NAME = "dashboard.pid"


# TODO: Combine get_*_pid, write_*_pid and stop_*_daemon functions


def get_config_root() -> Path:
    """Get the root of the configuration directory."""
    return Path.home() / ".computer_stats_daemon"


def get_config_file() -> Path:
    """Get the configuration file."""
    return get_config_root() / CONFIG_FILE_NAME


def read_config() -> configparser.ConfigParser:
    """Read the configuration file."""
    config_file = get_config_file()
    config = configparser.ConfigParser()
    if not config_file.exists():
        init_config()

    config.read(config_file)
    return config


def init_config() -> None:
    """Initialize the configuration directory."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)
    config_file = get_config_file()
    if not config_file.exists():
        with config_file.open("w") as f:
            f.write("[DEFAULT]\n")
            f.write("debug = false\n")
            f.write("sleep_seconds = 1\n")
            f.write("display_host = http://localhost:8889\n")


def is_pid_running(pid: int) -> bool:
    """Check if the PID is running."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def get_collector_daemon_pid() -> str:
    """Get the daemon PID."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)
    pid_file = config_root / COLLECTOR_PID_FILE_NAME
    if not pid_file.exists():
        return ""

    with pid_file.open() as f:
        return f.read().strip()


def write_collector_daemon_pid(pid: int) -> None:
    """Write the daemon PID."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)
    pid_file = config_root / COLLECTOR_PID_FILE_NAME
    with pid_file.open("w") as f:
        f.write(str(pid))


def stop_collector_daemon() -> int:
    """Stop the daemon."""
    daemon_pid = get_collector_daemon_pid()
    if daemon_pid != "" and is_pid_running(int(daemon_pid)):
        os.kill(int(daemon_pid), 15)
    else:
        return 1
    return 0


def get_dashboard_daemon_pid() -> str:
    """Get the daemon PID."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)
    pid_file = config_root / DASHBOARD_PID_FILE_NAME
    if not pid_file.exists():
        return ""

    with pid_file.open() as f:
        return f.read().strip()


def write_dashboard_daemon_pid(pid: int) -> None:
    """Write the daemon PID."""
    config_root = get_config_root()
    config_root.mkdir(parents=True, exist_ok=True)
    pid_file = config_root / DASHBOARD_PID_FILE_NAME
    with pid_file.open("w") as f:
        f.write(str(pid))


def stop_dashboard_daemon() -> int:
    """Stop the daemon."""
    daemon_pid = get_dashboard_daemon_pid()
    if daemon_pid != "" and is_pid_running(int(daemon_pid)):
        os.kill(int(daemon_pid), 15)
    else:
        return 1
    return 0
