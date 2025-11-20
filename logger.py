import logging
#import sys
from logging.handlers import RotatingFileHandler


def get_file_logger(
    name: str = __name__,
    filename: str = "multi_tool.log",
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:  # avoid adding handlers twice
        # Write logs to a rotating file
        handler = RotatingFileHandler(
            filename,
            mode="w",
            maxBytes=2_000_000,  # 2 MB per file
            backupCount=5,       # keep 5 old logs
            encoding="utf-8",
        )
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s — %(name)s — %(levelname)s — %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
