import logging
import sys


def setup_logger():
    logger = logging.getLogger("flights_api")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger


logger = setup_logger()


def report_error(error_message: str, extra_info: dict = {}):
    logger.error(error_message, extra=extra_info)


def report_info(info_message: str, extra_info: dict = {}):
    logger.info(info_message, extra=extra_info)
