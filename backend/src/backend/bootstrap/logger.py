import logging
from datetime import datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo

LoggingLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Standard LogRecord attributes that should not be included in extra fields
STANDARD_LOG_ATTRIBUTES = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
    "stack_info",
    "taskName",
}

EXCEPTION_ATTRIBUTES = {"exc_info", "exc_text"}


class TimeFormatter(logging.Formatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.kiev_tz = ZoneInfo("Europe/Kyiv")

    def formatTime(  # noqa: N802
        self, record: logging.LogRecord, date_fmt: str | None = None
    ) -> str:
        dt = datetime.fromtimestamp(record.created, tz=self.kiev_tz)
        if date_fmt:
            return dt.strftime(date_fmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _should_include_field(key: str, value: Any) -> bool:
        if key in STANDARD_LOG_ATTRIBUTES:
            return False

        if key in EXCEPTION_ATTRIBUTES:
            return value is not None

        return True

    def format(self, record: logging.LogRecord) -> str:
        formatted_message = super().format(record)

        extra_fields = []
        for key, value in record.__dict__.items():
            if self._should_include_field(key, value):
                extra_fields.append(f"{key}={value}")

        if extra_fields:
            formatted_message += f" | {', '.join(extra_fields)}"

        return formatted_message


def setup_logging(level: LoggingLevel = "INFO") -> None:
    level_map: dict[LoggingLevel, int] = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    numeric_level: int = level_map.get(level, logging.INFO)

    formatter = TimeFormatter(
        datefmt="%Y-%m-%d %H:%M:%S",
        fmt=(
            "[%(asctime)s.%(msecs)03d] "
            "%(funcName)20s "
            "%(module)s:%(lineno)d "
            "%(levelname)-8s - "
            "%(message)s"
        ),
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
