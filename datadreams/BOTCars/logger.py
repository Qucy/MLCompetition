import logging
from logging.handlers import TimedRotatingFileHandler


class GPTLogger:
    """
    GTP logger create log handlers
    """

    def __init__(self, name, level=logging.INFO, log_file=None):

        # Create a logger with the specifAied name and log level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        # Create a console handler to output log messages to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create a formatter to format log messages
        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)d, %(funcName)s] %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        self.logger.addHandler(console_handler)

        # If a log file is specified, create a file handler to save log messages to the file
        if log_file:
            file_handler = TimedRotatingFileHandler(
                log_file, when="D", interval=1, backupCount=7
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message):
        # Log a debug message
        self.logger.debug(message)

    def info(self, message):
        # Log an info message
        self.logger.info(message)

    def warning(self, message):
        # Log a warning message
        self.logger.warning(message)

    def error(self, message):
        # Log an error message
        self.logger.error(message)

    def critical(self, message):
        # Log a critical message
        self.logger.critical(message)

