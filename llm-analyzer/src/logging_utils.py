"""
Handles logging operations.
"""
import logging
import constants as c
formatter = logging.Formatter(c.LOG_FORMAT)


def setup_logger(name: str, log_file: str, level:int = logging.INFO):
    """
    Setups specialized logger object.

    :param name:
        File or module name
    :type name:
        str
    :param log_file:
        Output file, where the logs will be written
    :param level:
        Level of logging
    :type level:
        int
    :return:
        Logger object
    :rtype:
        logging.Logger
    """
    handler = logging.FileHandler(log_file, 'w', c.LOG_ENCODING)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
