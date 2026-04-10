import structlog
from config.settings import AppConfig
from domain.logger import Logger
from pathlib import Path
import logging


# Don't forget to keep logs.json file meaningful.
def setup_logging(logs_path: Path | str):
    # log_file = open(logs_path, "a", encoding="utf-8")
    structlog.configure(
        processors=[
            structlog.processors.StackInfoRenderer(),  # Stack strace, showing the exact source of errors.
            structlog.processors.format_exc_info,  # for Exceptions in JSON
            structlog.processors.add_log_level,  # Adding log level (info, warning, error)
            structlog.processors.TimeStamper(
                fmt="iso", utc=True
            ),  # Adding ISO timestamp
            structlog.processors.JSONRenderer(),  # Makes JSON outputs
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.INFO
        ),  # Profiling info and higher.
        # logger_factory = structlog.WriteLoggerFactory(file=log_file),    # Save in file instead of terminal
        cache_logger_on_first_use=True,  # Caching being used for optimization
    )


class StructLogger(Logger):
    def __init__(self, settings: AppConfig):
        setup_logging(logs_path="")
        self._logger = structlog.get_logger()

    def info(self, message: str, **kwargs):
        print(message)
        self._logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        print(message)
        self._logger.debug(message, **kwargs)

    def error(self, message: str, **kwargs):
        print(message)
        self._logger.error(message, **kwargs)

    def warn(self, message: str, **kwargs):
        # return super().warn(msg, **kwargs)
        print(message)
        self._logger.warn(message, **kwargs)

    def exception(self, message: str, **kwargs):
        print(message)
        self._logger.exception(message, **kwargs)
