import json
import os

# 读取 config.json（从项目根目录）
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_JSON_PATH = os.path.join(ROOT_DIR, "config.json")
if os.path.exists(CONFIG_JSON_PATH):
    with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
        json_config = json.load(f)
else:
    json_config = {}

def get_config():
    """
    优先从环境变量读取配置，如果环境变量不存在则从 config.json 读取。
    环境变量名与 config.json 字段一致。
    """
    config = dict(json_config)
    for key in config.keys():
        env_val = os.environ.get(key)
        if env_val is not None:
            # 尝试类型转换
            if isinstance(config[key], int):
                try:
                    env_val = int(env_val)
                except Exception:
                    pass
            elif isinstance(config[key], float):
                try:
                    env_val = float(env_val)
                except Exception:
                    pass
            elif isinstance(config[key], list):
                # 支持用逗号分隔的字符串转为列表
                env_val = [v.strip() for v in env_val.split(",")]
            config[key] = env_val
    return config 