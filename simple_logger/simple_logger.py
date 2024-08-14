import os
import json
import logging
from logging.handlers import RotatingFileHandler
import configparser

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger(*args, **kwargs)
        return cls._instance


    def _initialize_logger(self, config_file='config.ini',
                       log_directory=None,
                       log_filename='app.log',
                       json_log_filename='app.json',
                       colorize_console=True,
                       colorize_log=False,
                       colorize_json=False,
                       log_level='INFO',
                       log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                       date_format='%Y-%m-%d %H:%M:%S'):
        config = configparser.ConfigParser()
        
        if os.path.exists(config_file):
            config.read(config_file)
            log_directory = config.get('Logging', 'log_directory', fallback=log_directory)
            log_filename = config.get('Logging', 'log_filename', fallback=log_filename)
            json_log_filename = config.get('Logging', 'json_log_filename', fallback=json_log_filename)
            colorize_console = config.getboolean('Logging', 'colorize_console', fallback=colorize_console)
            colorize_log = config.getboolean('Logging', 'colorize_log', fallback=colorize_log)
            colorize_json = config.getboolean('Logging', 'colorize_json', fallback=colorize_json)
            log_level = config.get('Logging', 'log_level', fallback=log_level)
            log_format = config.get('Logging', 'log_format', fallback=log_format)
            date_format = config.get('Logging', 'date_format', fallback=date_format)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.get_log_level(log_level))


        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        if log_directory:
            log_file_path = os.path.join(log_directory, log_filename)
            json_log_file_path = os.path.join(log_directory, json_log_filename)

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        if colorize_log:
            log_formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            log_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(log_formatter)
        self.logger.addHandler(file_handler)

        if colorize_console:
            console_formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            console_formatter = logging.Formatter(log_format, datefmt=date_format)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        if colorize_json:
            json_formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            json_formatter = JSONFormatter(log_format, datefmt=date_format)
        json_file_handler = RotatingFileHandler(json_log_file_path, maxBytes=5*1024*1024, backupCount=5)
        json_file_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_file_handler)

    def get_log_level(self, log_level):
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(log_level.upper(), logging.DEBUG)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs, stacklevel=2)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs, stacklevel=2)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs, stacklevel=2)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs, stacklevel=2)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs, stacklevel=2)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'WARNING': '\033[93m',  # Yellow
        'INFO': '\033[92m',     # Green
        'DEBUG': '\033[94m',    # Blue
        'CRITICAL': '\033[95m', # Magenta
        'ERROR': '\033[91m',    # Red
        'RESET': '\033[0m',     # Reset
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            levelname_color = self.COLORS[levelname] + levelname + self.COLORS['RESET']
            record.levelname = levelname_color
        result = super().format(record)
        record.levelname = levelname  # Reset the levelname to the original value
        return result

class JSONFormatter(logging.Formatter):
    def format(self, record):
        original_levelname = record.levelname  # Save the original levelname
        log_record = {
            'time': self.formatTime(record, self.datefmt),
            'level': original_levelname,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName if record.funcName != '<module>' else 'main',
            'lineno': record.lineno,
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)
