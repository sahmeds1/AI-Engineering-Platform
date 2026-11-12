
import logging

from app.core.logging_config import configure_logging


def test_logging_configuration():
    configure_logging("DEBUG")

    logger = logging.getLogger()

    assert logger.level == logging.DEBUG


def test_invalid_log_level_defaults_to_info():
    configure_logging("INVALID")

    logger = logging.getLogger()

    assert logger.level == logging.INFO
