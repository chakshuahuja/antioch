import logging

from antioch.core import config

logger = logging.getLogger('antioch')

console = logging.StreamHandler()
console.setFormatter(logging.Formatter(
    fmt='%(asctime)s %(levelname)-5s %(name)-40s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
logger.addHandler(console)
logger.setLevel(config.DEFAULT_LOG_LEVEL)
logger.propagate = False