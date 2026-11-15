
import logging

from app.core.security import redact_secrets


class SecretRedactionFilter(logging.Filter):
    """
    Prevent common secret patterns from appearing in logs.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
            record.msg = redact_secrets(message)
            record.args = ()
        except Exception:
            # Fail closed: do not emit an unsanitized message.
            record.msg = "[LOG MESSAGE REDACTED]"
            record.args = ()

        return True


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=log_level.upper(),
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        force=True,
    )

    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        handler.addFilter(SecretRedactionFilter())
