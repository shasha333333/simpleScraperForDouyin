import logging
from colorlog import ColoredFormatter
from config import LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT, LOG_COLORS


def setup_logger():
    """配置彩色日志"""
    formatter = ColoredFormatter(
        LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        reset=True,
        log_colors=LOG_COLORS,
        secondary_log_colors={},
        style='%'
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)

    return logger