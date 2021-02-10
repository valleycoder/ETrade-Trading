import logging
from logging import Logger
from logging.handlers import RotatingFileHandler


class AppLogger:
    """ A basic logger.

        Attributes:

        Logger - Logger from logging module.

    """
    def __init__(self, logFilePathWithName:str, loggerName:str):
        """ Initialize the Logger with some predefined settings.

            Parameters:

            logFilePathWithName - log file path with name.

            loggerName - logger name for internal purposes.

        """

        self.Logger: Logger = logging.getLogger(loggerName)
        self.Logger.setLevel(logging.DEBUG)
        
        handler = RotatingFileHandler(logFilePathWithName, maxBytes=100 * 1024 * 1024, backupCount=3)
        FORMAT = "%(asctime)-15s %(message)s"
        fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
        handler.setFormatter(fmt)
        self.Logger.handlers.clear()
        self.Logger.addHandler(handler)
