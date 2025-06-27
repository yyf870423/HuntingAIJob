# TODO: 实现批量导入 Excel/简历到数据库和向量库 

import pandas as pd
import numpy as np
from app.logger import logger
from app.config import get_config
from app.resume_parser import parse_resume
from app.vector_store import add_candidate, collection
from app.llm import get_embedding_from_llm

config = get_config()
FIELDS = config["import_fields"]
EXPERIENCE_FIELD = config.get("experience_field", "经历")
UNIQUE_FIELDS = config.get("unique_fields", ["姓名", "行业", "学校", "专业"])

def make_candidate_id(item):
    return "_".join([str(item.get(f, "")).strip() for f in UNIQUE_FIELDS])

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
        result["经历"] = structured_exp
    else:
        result["经历"] = ""
    return result

def parse_excel_file(file_path, n):
    df = pd.read_excel(file_path)
    count = 0
    for idx, row in df.head(n).iterrows():
        item = parse_excel_row(row)
        if item["姓名"] == "":
            logger.warning(f"第{idx+2}行姓名为空，已跳过该记录。")
            continue
        # 1. 取元数据
        metadata = {field: item[field] for field in FIELDS}
        # 2. 取结构化经历文本
        exp_text = item["经历"]
        if not exp_text:
            logger.warning(f"第{idx+2}行经历为空，未存入向量库。")
            continue
        # 3. 向量化经历
        try:
            embedding = get_embedding_from_llm(exp_text)
            if not embedding or not isinstance(embedding, list) or not embedding or (isinstance(embedding[0], list) and not embedding[0]):
                logger.warning(f"第{idx+2}行 embedding 为空，未存入向量库。")
                continue
        except Exception as e:
            logger.warning(f"第{idx+2}行经历向量化失败: {e}")
            continue
        # 4. 用姓名+行业+学校+专业生成 candidate_id
        candidate_id = make_candidate_id(item)
        existing = collection.get(ids=[candidate_id])
        if existing["ids"] and candidate_id in existing["ids"]:
            print(f"{candidate_id} 已存在，进行更新操作。")
        else:
            print(f"{candidate_id} 为新增数据，进行写入操作。")
        # 5. 存入 Chroma
        add_candidate(candidate_id, embedding, metadata)
        count += 1
        print(f"第{count}条已存入 Chroma：")
        print({"id": candidate_id, "metadata": metadata, "经历": exp_text})
        print("-" * 40)

if __name__ == "__main__":
    parse_excel_file("data/data_source.xlsx", 30) 