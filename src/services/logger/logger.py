from config import LOG_PATH
from logging.handlers import TimedRotatingFileHandler
from config import LOG_ERROR_FILENAME
from config import LOG_FILENAME
import logging

def setup_logger():
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Handler per log generale
    fh = TimedRotatingFileHandler(
        LOG_PATH / LOG_FILENAME,
        when="midnight",     # ruota a mezzanotte
        interval=1,          # ogni 1 giorno
        backupCount=7,       # mantiene 7 file, cancella i più vecchi
        encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Handler solo per errori
    eh = logging.FileHandler(LOG_PATH / LOG_ERROR_FILENAME)
    eh.setLevel(logging.ERROR)
    eh.setFormatter(fmt)

    # Console opzionale
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(eh)
    logger.addHandler(ch)
    return logger

logger = setup_logger()