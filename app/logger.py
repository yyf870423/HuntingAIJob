import logging
import os

LOG_FORMAT = '%(asctime)s | %(levelname)s | %(message)s'
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "hunting_ai_job.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # 控制台
        logging.FileHandler(LOG_FILE, encoding='utf-8')  # 文件
    ]
)
logger = logging.getLogger("HuntingAIJob") 