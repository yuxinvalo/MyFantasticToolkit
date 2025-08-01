import logging
import os.path
import sys
import time

# log_dir = os.path.join(os.path.dirname(__file__), "logs")


def _reset_logger(log):
    for handler in log.handlers:
        handler.close()
        log.removeHandler(handler)
        del handler
    log.handlers.clear()
    log.propagate = False
    console_handle = logging.StreamHandler(sys.stdout)
    console_handle.setFormatter(
        logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    filepath = os.path.join(os.path.dirname(__file__), '../logs')
    logFilename = os.path.join(filepath, time.strftime("%Y_%m_%d", time.localtime()) + '.log')
    file_handle = logging.FileHandler(logFilename, encoding="utf-8")
    file_handle.setFormatter(
        logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    log.addHandler(file_handle)
    log.addHandler(console_handle)


def _get_logger():
    log = logging.getLogger("log")
    _reset_logger(log)
    log.setLevel(logging.DEBUG)
    return log


# 日志句柄
logger = _get_logger()