import logging
import sys


def get_logger(name: str, log_level: int = logging.INFO) -> logging.Logger:
    """Конфигурирует и возвращает logger с указанным именем"""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
