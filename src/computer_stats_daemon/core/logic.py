import time
from collections.abc import Callable

import psutil


def get_cpu_usage() -> float:
    """Get the current CPU usage."""
    return psutil.cpu_percent(interval=0.1, percpu=False)


def get_memory_usage() -> float:
    """Get the current memory usage."""
    return psutil.virtual_memory().percent


def collect_stats() -> dict:
    """Collect the current stats."""
    return {
        "cpu": get_cpu_usage(),
        "memory": get_memory_usage(),
    }


def start_stats_emitter(poll_interval: int, callback: Callable[[dict], None]) -> None:
    """Start the stats emitter."""
    while True:
        try:
            stats = collect_stats()
            callback(stats)
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            break
