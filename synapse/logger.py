import logging
import sys


class Logger(logging.Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        
        # Format string without applying color yet
        format_string = "[%(levelname_color)s] [%(name)s] [%(asctime)s] - %(message)s"

        handler.setFormatter(ColorFormatter(format_string))
        self.addHandler(handler)


class ColorFormatter(logging.Formatter):
    # Color mapping for different log levels
    COLOR_MAPPING = {
        "DEBUG": "\033[36m",   # Cyan
        "INFO": "\033[32m",    # Green
        "WARNING": "\033[33m", # Yellow
        "ERROR": "\033[31m",   # Red
        "CRITICAL": "\033[35m" # Magenta
    }

    def format(self, record):
        # Get the log level color based on the levelname
        levelname_color = self.COLOR_MAPPING.get(record.levelname, "\033[37m")
        
        # Modify the record to include the color
        record.levelname_color = f"{levelname_color}{record.levelname}\033[0m"        

        # Format the message using the base class format method
        return super().format(record)
