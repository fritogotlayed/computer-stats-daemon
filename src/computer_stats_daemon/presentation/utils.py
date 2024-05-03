from __future__ import annotations

import logging
import sys


def setup_logging(level: int | str) -> None:
    """Set up logging."""
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s" if level == logging.DEBUG else "%(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
