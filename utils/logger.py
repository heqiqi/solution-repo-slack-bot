import logging, logging.config

logging.config.fileConfig('logger.conf')
# 获取 logger
logger = logging.getLogger('application')