from app.logger import logger
from app.resume_parser import parse_resume
from app.vector_store import add_candidate, collection
from app.llm import get_embedding_from_llm
from app.config import get_config

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
            # print(f"[single_import] 结构化经历失败: {e}")
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
    # 向量化经历
    exp_text = item.get("经历", "")
    if not exp_text:
        logger.warning("[single_import] 经历字段为空，无法向量化")
        # print("[single_import] 经历字段为空，无法向量化")
        raise ValueError("经历字段为空，无法向量化")
    logger.info("[single_import] 开始向量化经历")
    print("[single_import] 开始向量化经历")
    embedding = get_embedding_from_llm(exp_text)
    logger.info("[single_import] 向量化完成，写入Chroma")
    # print("[single_import] 向量化完成，写入Chroma")
    # 写入Chroma
    add_candidate(candidate_id, embedding, item)
    logger.info(f"[single_import] {op_type}成功: {candidate_id}")
    # print(f"[single_import] {op_type}成功: {candidate_id}")
    return op_type, candidate_id 