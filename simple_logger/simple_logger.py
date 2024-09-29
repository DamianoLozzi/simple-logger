from logging.handlers import RotatingFileHandler
import configparser
import inspect
import logging
import json
import os

config = configparser.ConfigParser(interpolation=None)
config.read('config.ini')

try:
    LOG_DIRECTORY = config.get('LOGGING', 'LOG_DIRECTORY', fallback=None)
    LOG_FILENAME = config.get('LOGGING', 'LOG_FILENAME', fallback='app.log')
    JSON_LOG_FILENAME = config.get('LOGGING', 'JSON_LOG_FILENAME', fallback='app_log.json')
    COLORIZE_CONSOLE = config.getboolean('LOGGING', 'CONSOLE_COLORIZE', fallback=True)
    COLORIZE_LOG = config.getboolean('LOGGING', 'LOG_COLORIZE', fallback=False)
    COLORIZE_JSON = config.getboolean('LOGGING', 'JSON_COLORIZE', fallback=False)
    LOG_LEVEL = config.get('LOGGING', 'LOG_LEVEL', fallback='DEBUG')
    LOG_FORMAT = config.get('LOGGING', 'LOG_FORMAT', fallback='%(asctime)s | %(levelname)s\t| %(filename)s \t|%(lineno)d\t| %(message)s')
    DATE_FORMAT = config.get('LOGGING', 'DATE_FORMAT', fallback='%Y-%m-%d %H:%M:%S')
except configparser.NoSectionError:
    print('No LOGGING section found in config.ini. Using default values.')
    LOG_DIRECTORY = None
    LOG_FILENAME = 'app.log'
    JSON_LOG_FILENAME = 'app_log.json'
    COLORIZE_CONSOLE = True
    COLORIZE_LOG = False
    COLORIZE_JSON = False
    LOG_LEVEL = 'DEBUG'
    LOG_FORMAT = '%(asctime)s | %(levelname)s\t| %(filename)s \t|%(lineno)d\t| %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class Logger(logging.Logger):
    def __init__(self):
        super().__init__(__name__)
        self._initialize_logger()
        
    def _initialize_logger(self, log_directory=LOG_DIRECTORY,
                           log_filename=LOG_FILENAME,
                           json_log_filename=JSON_LOG_FILENAME,
                           colorize_console=COLORIZE_CONSOLE,
                           colorize_log=COLORIZE_LOG,
                           colorize_json=COLORIZE_JSON,
                           log_level=LOG_LEVEL,
                           log_format=LOG_FORMAT,
                           date_format=DATE_FORMAT):
        self.setLevel(self.get_log_level(log_level))
           
        file_logging = False if log_directory is None else True

        if file_logging is True:
            log_file_path = os.path.join(log_directory, log_filename)
            json_log_file_path = os.path.join(log_directory, json_log_filename)

            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
                
            if self.hasHandlers():
                self.handlers.clear()

            if colorize_log:
                log_formatter = ColoredFormatter(log_format, datefmt=date_format)
            else:
                log_formatter = logging.Formatter(log_format, datefmt=date_format)
            file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=5)
            file_handler.setFormatter(log_formatter)
            self.addHandler(file_handler)
            
            if colorize_json:
                json_formatter = ColoredFormatter(log_format, datefmt=date_format)
            else:
                json_formatter = logging.Formatter(log_format, datefmt=date_format)
            json_file_handler = RotatingFileHandler(json_log_file_path, maxBytes=5*1024*1024, backupCount=5)
            json_file_handler.setFormatter(json_formatter)
            self.addHandler(json_file_handler)

        if colorize_console:
            console_formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            console_formatter = logging.Formatter(log_format, datefmt=date_format)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        self.addHandler(console_handler)
        
    def get_log_level(self, log_level):
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(log_level.upper(), logging.DEBUG)  
    

        
 

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
