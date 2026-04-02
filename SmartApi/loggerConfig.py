import logging
import os

LOG_DIR = "logs"
LOG_FILE = "app.log"

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# ANSI color codes
LOG_COLORS = {
    'DEBUG': "\033[32m",     # Green
    'INFO': "\033[32m",      # Green
    'WARNING': "\033[33m",   # Yellow
    'ERROR': "\033[31m",     # Red
    'CRITICAL': "\033[41m",  # Red background
    'RESET': "\033[0m"       # Reset
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_color = LOG_COLORS.get(record.levelname, LOG_COLORS['RESET'])
        reset = LOG_COLORS['RESET']
        message = super().format(record)
        return f"{log_color}{message}{reset}"


def get_logger(name: str, level: str = "WARNING") -> logging.Logger:
    """
    Creates and returns a logger instance that logs messages at the specified level and above.
    Logs are saved in logs/app.log and also printed to console with color.

    Parameters:
        name (str): Logger name.
        level (str): Logging level (e.g. 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
                     Defaults to 'WARNING'.

    Returns:
        logging.Logger: Configured logger instance.
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.WARNING))

    if not logger.hasHandlers():
        # File handler
        log_path = os.path.join(LOG_DIR, LOG_FILE)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(getattr(logging, level.upper(), logging.WARNING))

        # Console handler with color
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper(), logging.WARNING))

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        color_formatter = ColorFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(color_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
