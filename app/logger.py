import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "hunting_ai_job.log")

os.makedirs(LOG_DIR, exist_ok=True)

# 日志文件每天分割，保留30天
file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight', interval=1, backupCount=30, encoding='utf-8')
file_handler.suffix = "%Y-%m-%d"
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        stream_handler,  # 控制台
        file_handler     # 按日期分割的文件
    ]
)
logger = logging.getLogger("HuntingAIJob") 