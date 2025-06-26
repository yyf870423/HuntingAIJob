# TODO: 实现批量导入 Excel/简历到数据库和向量库 

import pandas as pd
import numpy as np
from app.logger import logger
from app.config import get_config
from app.resume_parser import parse_resume

config = get_config()
FIELDS = config["import_fields"]
EXPERIENCE_FIELD = config.get("experience_field", "经历")

def parse_excel_row(row):
    """将一行Excel数据转为结构化字典，空值输出为空字符串，并结构化经历字段"""
    result = {}
    for field in FIELDS:
        value = row.get(field, "")
        if pd.isna(value):
            value = ""
        result[field] = value
    # 结构化经历字段
    experience_text = row.get(EXPERIENCE_FIELD, "")
    if pd.isna(experience_text):
        experience_text = ""
    if experience_text:
        try:
            structured_exp = parse_resume(experience_text)
        except Exception as e:
            logger.warning(f"结构化经历失败: {e}")
            structured_exp = ""
        result["结构化经历"] = structured_exp
    else:
        result["结构化经历"] = ""
    return result

def parse_excel_file(file_path, n=5):
    df = pd.read_excel(file_path)
    count = 0
    for idx, row in df.head(n).iterrows():
        item = parse_excel_row(row)
        if item["姓名"] == "":
            logger.warning(f"第{idx+2}行姓名为空，已跳过该记录。")
            continue
        count += 1
        print(f"第{count}条结果：")
        print(item)
        print("-" * 40)

if __name__ == "__main__":
    parse_excel_file("data/data_source.xlsx", n=5) 