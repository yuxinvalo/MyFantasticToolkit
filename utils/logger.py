import logging
import os.path
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# log_dir = os.path.join(os.path.dirname(__file__), "logs")


def _get_logs_dir():
    """获取日志目录路径，支持打包后的环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境：使用可执行文件所在目录
        return Path(sys.executable).parent / "logs"
    else:
        # 开发环境：使用相对路径
        return Path(__file__).parent.parent / "logs"


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
    logs_dir = _get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)  # 确保日志目录存在
    logFilename = str(logs_dir / (time.strftime("%Y_%m_%d", time.localtime()) + '.log'))
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
    log.setLevel(logging.INFO)
    return log


def cleanup_old_logs():
    """清理五天前的日志文件"""
    try:
        logs_dir = _get_logs_dir()
        if not logs_dir.exists():
            return
        
        # 计算五天前的时间戳
        five_days_ago = datetime.now() - timedelta(days=5)
        
        # 查找所有日志文件
        log_files = list(logs_dir.glob("*.log"))
        
        deleted_count = 0
        for log_file in log_files:
            try:
                # 获取文件修改时间
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                # 如果文件超过五天，删除它
                if file_mtime < five_days_ago:
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f"[CLEANUP] Deleted old log file: {log_file.name}")
            except Exception as e:
                logger.warning(f"[CLEANUP] Failed to delete log file {log_file}: {e}")
        
        if deleted_count > 0:
            logger.info(f"[CLEANUP] Cleaned up {deleted_count} old log files")
        else:
            logger.info("[CLEANUP] No old log files to clean up")
            
    except Exception as e:
        logger.error(f"[CLEANUP] Log cleanup failed: {e}")


# 日志句柄
logger = _get_logger()