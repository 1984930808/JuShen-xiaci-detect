"""统一日志系统。"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# 日志目录
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件名（按日期）
LOG_FILE = LOG_DIR / f"inspection_{datetime.now().strftime('%Y%m%d')}.log"


def setup_logger(name: str = "jushen", level=logging.INFO) -> logging.Logger:
    """
    配置日志系统。
    
    Args:
        name: 日志器名称
        level: 日志级别
        
    Returns:
        配置好的Logger对象
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 控制台处理器（简洁格式）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器（详细格式）
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# 全局日志器
logger = setup_logger()


def log_inspection_start(sample_id: str):
    """记录检测开始。"""
    logger.info("=" * 60)
    logger.info(f"开始检测样品: {sample_id}")
    logger.info("=" * 60)


def log_inspection_complete(sample_id: str, result: str, elapsed: float):
    """记录检测完成。"""
    logger.info(f"样品 {sample_id} 检测完成: {result} (耗时: {elapsed:.2f}s)")
    logger.info("=" * 60)


def log_step(step_name: str, status: str, message: str = ""):
    """记录检测步骤。"""
    logger.info(f"[{step_name}] {status}" + (f" - {message}" if message else ""))


def log_error(error: Exception, context: str = ""):
    """记录错误信息。"""
    logger.error(f"错误发生{(' - ' + context) if context else ''}: {type(error).__name__}: {str(error)}")
    logger.debug("详细错误信息:", exc_info=True)
