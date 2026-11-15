
import re


SECRET_PATTERNS = [
    # OpenAI-style secret keys
    (
        re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
        "[REDACTED]",
    ),

    # Bearer tokens
    (
        re.compile(
            r"(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]+"
        ),
        r"\1[REDACTED]",
    ),

    # Common key=value formats
    (
        re.compile(
            r"(?i)(api[_-]?key\s*[=:]\s*)"
            r"[^&\s,;]+"
        ),
        r"\1[REDACTED]",
    ),

    # Common password=value formats
    (
        re.compile(
            r"(?i)(password\s*[=:]\s*)"
            r"[^&\s,;]+"
        ),
        r"\1[REDACTED]",
    ),
]


def redact_secrets(value: str) -> str:
    """
    Mask common secret patterns before logging text.
    """
    sanitized = value

    for pattern, replacement in SECRET_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized
