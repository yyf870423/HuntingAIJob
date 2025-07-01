from app.logger import logger
from app.resume_parser import parse_resume
from app.vector_store import add_candidate, collection
from app.llm import get_embedding_from_llm
from app.config import get_config
import json

config = get_config()
UNIQUE_FIELDS = config.get("unique_fields", ["姓名", "行业", "学校", "专业"])


def make_candidate_id(item):
    candidate_id = "_".join([str(item.get(f, "")).strip() for f in UNIQUE_FIELDS])
    logger.info(f"[single_import] 生成 candidate_id: {candidate_id}")
    print(f"[single_import] 生成 candidate_id: {candidate_id}")
    return candidate_id


def parse_single_row(row):
    """
    结构化单条简历数据，row为dict，返回结构化dict
    """
    result = row.copy()
    exp_text = row.get("经历", "")
    if exp_text:
        try:
            structured_exp = parse_resume(exp_text)
            logger.info("[single_import] 结构化经历成功")
            # print("[single_import] 结构化经历成功")
        except Exception as e:
            logger.warning(f"结构化经历失败: {e}")
            # print(f"结构化经历失败: {e}")
            structured_exp = ""
        result["经历"] = structured_exp
    else:
        logger.warning("[single_import] 经历字段为空")
        # print("[single_import] 经历字段为空")
        result["经历"] = ""
    return result


def single_import(row):
    """
    row: dict，包含所有字段（含经历原文）
    返回: (op_type, candidate_id)
    """
    logger.info(f"[single_import] 开始处理 row: {row}")
    # print(f"[single_import] 开始处理 row: {row}")
    item = parse_single_row(row)
    candidate_id = make_candidate_id(item)
    # 检查插入/更新
    existing = collection.get(ids=[candidate_id])
    if existing["ids"] and candidate_id in existing["ids"]:
        op_type = "更新"
        logger.info(f"[single_import] {candidate_id} 已存在，执行更新操作")
        # print(f"[single_import] {candidate_id} 已存在，执行更新操作")
    else:
        op_type = "插入"
        logger.info(f"[single_import] {candidate_id} 为新增数据，执行插入操作")
        # print(f"[single_import] {candidate_id} 为新增数据，执行插入操作")
    # 结构化经历
    exp_struct = item.get("经历", {})
    print("[DEBUG] 结构化经历内容 exp_struct:", json.dumps(exp_struct, ensure_ascii=False, indent=2))
    if not exp_struct or not isinstance(exp_struct, dict):
        logger.warning(f"[single_import] 结构化经历字段为空或格式不对，无法向量化，candidate_id={candidate_id}, row={json.dumps(row, ensure_ascii=False)}")
        raise ValueError("结构化经历字段为空或格式不对，无法向量化")
    # 多维度分别向量化，最后批量 upsert
    ids = []
    embeddings = []
    metadatas = []
    dim_fields = ["technical_skills", "experience", "projects", "academic_background", "bonus_items"]
    for dim in dim_fields:
        dim_content = exp_struct.get(dim, "")
        print(f"[DEBUG] {dim} 内容:", dim_content)
        if not dim_content:
            logger.warning(f"[single_import] {dim} 为空，依然入库，candidate_id={candidate_id}, row={json.dumps(row, ensure_ascii=False)}")
            # embedding 用全零向量，长度与正常 embedding 一致
            try:
                zero_embedding = [0.0] * len(get_embedding_from_llm("test"))
            except Exception:
                zero_embedding = [0.0] * 768  # 默认 768 维
            ids.append(f"{candidate_id}_{dim}")
            meta = {}
            for base_field in config.get("import_fields", []):
                meta[base_field] = row.get(base_field, "")
            metadatas.append(meta)
            embeddings.append(zero_embedding)
            continue
        if isinstance(dim_content, dict) or isinstance(dim_content, list):
            dim_text = json.dumps(dim_content, ensure_ascii=False)
        else:
            dim_text = str(dim_content)
        logger.info(f"[single_import] 开始向量化 {dim}, candidate_id={candidate_id}")
        print(f"[single_import] 开始向量化 {dim}")
        try:
            embedding = get_embedding_from_llm(dim_text)
        except Exception as e:
            logger.error(f"[single_import] 向量化 {dim} 失败, candidate_id={candidate_id}, 原因: {e}, 内容: {dim_text}")
            # 失败时也用全零向量
            try:
                zero_embedding = [0.0] * len(get_embedding_from_llm("test"))
            except Exception:
                zero_embedding = [0.0] * 768
            ids.append(f"{candidate_id}_{dim}")
            meta = {}
            for base_field in config.get("import_fields", []):
                meta[base_field] = row.get(base_field, "")
            metadatas.append(meta)
            embeddings.append(zero_embedding)
            continue
        ids.append(f"{candidate_id}_{dim}")
        embeddings.append(embedding)
        meta = {}
        for base_field in config.get("import_fields", []):
            meta[base_field] = row.get(base_field, "")
        metadatas.append(meta)
    if ids:
        collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas)
        for i in ids:
            print(f"[single_import] {op_type}成功: {i}")
    return op_type, candidate_id 