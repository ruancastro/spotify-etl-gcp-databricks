"""Logging utility using standard library only."""

# src/utils/logger.py
import logging
import json
import sys
from typing import Optional


def get_logger(
    name: str,
    level: Optional[str] = None,
    log_to_stdout: bool = True,
) -> logging.Logger:
    """Creates a JSON-structured logger using only standard library.

    Args:
        name: Module name (use __name__).
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR'). Defaults to INFO.
        log_to_stdout: If True, logs to stdout (ideal for Cloud Run).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level or "INFO")
    logger.propagate = False

    if logger.handlers:
        return logger

    class JsonFormatter(logging.Formatter):
        """Custom JSON formatter for log records."""

        def format(self, record):
            log_data = {
                "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
                "level": record.levelname,
                "logger": record.name,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "message": record.getMessage(),
                "app": "christmas_pulse",
                "env": "production",
            }
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_data, ensure_ascii=False)

    formatter = JsonFormatter()

    if log_to_stdout:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
