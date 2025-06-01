from logging.handlers import RotatingFileHandler
import configparser
import logging
import json
import os
from typing import Optional


def _get_env_or_config_str(section: str, option: str, env_var: str, fallback: str, parser: configparser.ConfigParser) -> str:
    val = os.getenv(env_var)
    if val:
        return val
    return parser.get(section, option, fallback=fallback)


def _get_env_or_config_bool(section: str, option: str, env_var: str, fallback: bool, parser: configparser.ConfigParser) -> bool:
    val = os.getenv(env_var)
    if val is not None:
        return val.strip().lower() not in ('0', 'false', '')
    return parser.getboolean(section, option, fallback=fallback)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m',     # Reset
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            colored = self.COLORS[levelname] + levelname + self.COLORS['RESET']
            record.levelname = colored
        formatted = super().format(record)
        record.levelname = levelname  # ripristina
        return formatted


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'time': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName if record.funcName != '<module>' else 'main',
            'lineno': record.lineno,
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


def _resolve_log_level(level_str: str) -> int:
    mapping = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return mapping.get(level_str.upper(), logging.DEBUG)


class Logger(logging.Logger):
    def __init__(self):
        super().__init__(__name__)
        self._load_config()
        self._initialize_logger()

    def _load_config(self):
        self.parser = configparser.ConfigParser(interpolation=None)
        if os.path.isfile('config.ini'):
            self.parser.read('config.ini')
        else:
            self.parser.read_dict({'LOGGING': {}})  # se manca, usiamo dict vuoto

        self.LOG_DIRECTORY     = _get_env_or_config_str(
            'LOGGING', 'LOG_DIRECTORY', 'LOG_DIRECTORY', '', self.parser)
        self.LOG_FILENAME      = _get_env_or_config_str(
            'LOGGING', 'LOG_FILENAME', 'LOG_FILENAME', 'app.log', self.parser)
        self.JSON_LOG_FILENAME = _get_env_or_config_str(
            'LOGGING', 'JSON_LOG_FILENAME', 'JSON_LOG_FILENAME', 'app_log.json', self.parser)
        self.COLORIZE_CONSOLE  = _get_env_or_config_bool(
            'LOGGING', 'CONSOLE_COLORIZE', 'CONSOLE_COLORIZE', True, self.parser)
        self.COLORIZE_LOG      = _get_env_or_config_bool(
            'LOGGING', 'LOG_COLORIZE', 'LOG_COLORIZE', False, self.parser)
        self.COLORIZE_JSON     = _get_env_or_config_bool(
            'LOGGING', 'JSON_COLORIZE', 'JSON_COLORIZE', False, self.parser)
        self.LOG_LEVEL         = _get_env_or_config_str(
            'LOGGING', 'LOG_LEVEL', 'LOG_LEVEL', 'DEBUG', self.parser)
        self.LOG_FORMAT        = _get_env_or_config_str(
            'LOGGING', 'LOG_FORMAT', 'LOG_FORMAT', '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s', self.parser)
        self.DATE_FORMAT       = _get_env_or_config_str(
            'LOGGING', 'DATE_FORMAT', 'DATE_FORMAT', '%Y-%m-%d %H:%M:%S', self.parser)

    def _initialize_logger(self):
        self.setLevel(_resolve_log_level(self.LOG_LEVEL))

        if self.hasHandlers():
            for h in list(self.handlers):
                self.removeHandler(h)

        if self.LOG_DIRECTORY:
            os.makedirs(self.LOG_DIRECTORY, exist_ok=True)
            log_path = os.path.join(self.LOG_DIRECTORY, self.LOG_FILENAME)
            json_log_path = os.path.join(self.LOG_DIRECTORY, self.JSON_LOG_FILENAME)

            file_formatter = (
                ColoredFormatter(self.LOG_FORMAT, datefmt=self.DATE_FORMAT)
                if self.COLORIZE_LOG else logging.Formatter(self.LOG_FORMAT, datefmt=self.DATE_FORMAT)
            )
            file_handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=5)
            file_handler.setFormatter(file_formatter)
            self.addHandler(file_handler)

            json_formatter = (
                ColoredFormatter(self.LOG_FORMAT, datefmt=self.DATE_FORMAT)
                if self.COLORIZE_JSON else JSONFormatter(datefmt=self.DATE_FORMAT)
            )
            json_handler = RotatingFileHandler(json_log_path, maxBytes=5*1024*1024, backupCount=5)
            json_handler.setFormatter(json_formatter)
            self.addHandler(json_handler)

        console_formatter = (
            ColoredFormatter(self.LOG_FORMAT, datefmt=self.DATE_FORMAT)
            if self.COLORIZE_CONSOLE else logging.Formatter(self.LOG_FORMAT, datefmt=self.DATE_FORMAT)
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        self.addHandler(console_handler)

log = Logger()