import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logging(app=None):
    """
    Centralized logging configuration.
    - Console handler always enabled
    - Rotating file handlers enabled if LOG_FILE set
    """
    log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Formatter
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(log_level)
    console.setFormatter(formatter)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console)

    # File handler (optional)
    log_file = os.environ.get('LOG_FILE')
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        max_bytes = int(os.environ.get('LOG_MAX_BYTES', str(10 * 1024 * 1024)))  # 10MB
        backup_count = int(os.environ.get('LOG_BACKUP_COUNT', '5'))
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Error-only file handler (optional separate file)
    error_file = os.environ.get('LOG_ERROR_FILE')
    if error_file:
        os.makedirs(os.path.dirname(error_file), exist_ok=True)
        err_handler = RotatingFileHandler(error_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        err_handler.setLevel(logging.ERROR)
        err_handler.setFormatter(formatter)
        logger.addHandler(err_handler)


