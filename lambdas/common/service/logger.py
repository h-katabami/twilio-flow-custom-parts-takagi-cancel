import logging
import sys
import traceback

logger = logging.getLogger()
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def info(msg: str, **kwargs) -> None:
    if kwargs:
        msg = f"{msg} {kwargs}"
    logger.info(msg)


def warn(msg: str, **kwargs) -> None:
    if kwargs:
        msg = f"{msg} {kwargs}"
    logger.warning(msg)


def error(msg: str, exc=None, **kwargs) -> None:
    if kwargs:
        msg = f"{msg} {kwargs}"
    logger.error(msg)
    if exc:
        logger.error(traceback.format_exc())
