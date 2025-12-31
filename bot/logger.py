import logging
from .config import config


def setup_logging():
    level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # Reduce noise from underlying libraries
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)


logger = logging.getLogger('duality')
