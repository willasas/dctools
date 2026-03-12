"""日志配置模块"""
import logging
import os
from datetime import datetime

# 创建logs目录
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(logs_dir, exist_ok=True)

# 创建日志文件
log_file = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 创建logger实例
def get_logger(name):
    """获取logger实例"""
    return logging.getLogger(name)
