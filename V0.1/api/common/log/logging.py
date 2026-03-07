"""
Logging configuration module for the electricity bill calculator.

This module provides functions to initialize and configure logging for the
application using a JSON configuration file. It ensures that logging is set
up only once and provides a convenient interface to obtain loggers.
"""
import json
import logging
import logging.config
from pathlib import Path


def find_project_root(
    start: Path = Path(__file__), marker: str = "pyproject.toml"
) -> Path:
    """Find the project root directory by looking for a marker file."""
    for parent in start.resolve().parents:
        if (parent / marker).exists():
            return parent
    raise RuntimeError(f"Project root not found (no {marker} found)")


LOG_FILE = find_project_root().joinpath('build', 'logs', 'app.log')
LOGGING_CONFIG_FILE = (
    find_project_root().joinpath(
        'api', 'common', 'log', 'conf', 'logging_config.json'
    )
)


def setup_logging():
    """Set up logging configuration from a JSON file."""
    # Check if logging has already been configured
    if logging.root.handlers:
        return

    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOGGING_CONFIG_FILE, 'r', encoding='utf-8') as config_file:
        config_dict = json.load(config_file)
        for handler in config_dict.get('handlers', {}).values():
            if handler.get('class') == 'logging.FileHandler':
                handler['filename'] = str(LOG_FILE)

        logging.config.dictConfig(config_dict)

        logger = logging.getLogger(__name__)
        logger.debug("Logging initialized. Log file at: %s", LOG_FILE)


def set_file_handler_level(level: str = 'DEBUG') -> None:
    """Adjust the file handler's log level at runtime."""

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    for handler in logging.root.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setLevel(numeric_level)
            logging.getLogger(__name__).debug(
                "File handler log level set to %s", level.upper()
            )
            return
    logging.getLogger(__name__).warning(
        "No FileHandler found on root logger; "
        "file log level was not changed."
    )


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Get a logger with the specified name, ensuring logging is set up.
    """
    if not logging.root.handlers:
        setup_logging()

    return logging.getLogger(name)
