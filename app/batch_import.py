# TODO: 实现批量导入 Excel/简历到数据库和向量库 

from app.logger import logger
from app.config import get_config
from app.resume_parser import parse_resume
from app.vector_store import collection
from app.single_import import single_import
import pandas as pd
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

config = get_config()
FIELDS = config["import_fields"]
EXPERIENCE_FIELD = config.get("experience_field", "经历")
UNIQUE_FIELDS = config.get("unique_fields", ["姓名", "行业", "学校", "专业"])

def make_candidate_id(item):
    return "_".join([str(item.get(f, "")).strip() for f in UNIQUE_FIELDS])

def parse_excel_row(row):
    """将一行Excel数据转为结构化字典，空值输出为空字符串"""
    result = {}
    for field in FIELDS:
        value = row.get(field, "")
        if pd.isna(value):
            value = ""
        result[field] = value
    # 结构化经历字段（原文）
    experience_text = row.get(EXPERIENCE_FIELD, "")
    if pd.isna(experience_text):
        experience_text = ""
    result["经历"] = experience_text
    return result

def parse_excel_file(file_path, n=None, task_id=None, max_workers=32):
    import sys, os
    print("parse_excel_file收到文件路径：", file_path, "存在吗？", os.path.exists(file_path))
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print("读取Excel失败：", e)
        raise
    count = 0
    # 动态import避免循环依赖
    items = list(df.iterrows()) if n is None else list(df.head(n).iterrows())

    def import_one(idx_row):
        idx, row = idx_row
        # 检查是否被取消（文件持久化方式）
        if task_id:
            try:
                from app.batch_import_async import load_tasks
                tasks = load_tasks()
                if tasks.get(task_id, {}).get("cancel"):
                    print(f"任务{task_id}被取消，中断导入。")
                    return "cancelled"
            except Exception as e:
                print(f"检查任务取消状态失败: {e}")
        item = parse_excel_row(row)
        if item["姓名"] == "":
            logger.warning(f"第{idx+2}行姓名为空，已跳过该记录。")
            return None
        try:
            op_type, candidate_id = single_import(item)
            print(f"第{idx+1}条（{op_type}）：{candidate_id}")
            return True
        except Exception as e:
            logger.warning(f"第{idx+2}行导入失败: {e}")
            print(f"第{idx+2}行导入失败: {e}")
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(import_one, idx_row) for idx_row in items]
        for future in as_completed(futures):
            result = future.result()
            if result == "cancelled":
                # 发现取消，立即终止后续任务
                for f in futures:
                    f.cancel()
                break
            if result:
                count += 1
    return count

if __name__ == "__main__":
    parse_excel_file("data/data_source.xlsx", 30) 