from app.llm import call_gpt, get_embedding_from_llm
import os
import json

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt", "resume_parser_prompt.txt")

def parse_resume(resume_text):
    """调用 LLM 对简历进行结构化解析，返回结构化字段（dict）。"""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    full_prompt = f"{system_prompt}\n\n简历/经历:\n{resume_text.strip()}"
    result = call_gpt(full_prompt)
    try:
        resume_struct = json.loads(result)
    except Exception as e:
        print("[ERROR] LLM output is not valid JSON!", e)
        print(result)
        raise
    return resume_struct

if __name__ == "__main__":
    import pandas as pd
    df = pd.read_excel("data/data_source.xlsx")
    # 取第一行非空有效数据
    for idx, row in df.iterrows():
        # 只要经历字段非空就用
        if row.get("经历") and isinstance(row.get("经历"), str) and row.get("经历").strip():
            row_dict = row.to_dict()
            break
    else:
        raise ValueError("data_source.xlsx 未找到有效简历数据！")
    from app.single_import import single_import
    op_type, candidate_id = single_import(row_dict)
    print(f"\n[TEST] {op_type}成功: {candidate_id} (多维度已写入 Chroma)")
    # 展示结构化解析的五个维度
    dim_fields = ["technical_skills", "experience", "projects", "academic_background", "bonus_items"]
    resume_struct = row_dict.get("经历")
    if isinstance(resume_struct, dict):
        filtered_struct = {k: resume_struct.get(k, None) for k in dim_fields}
        print("\n【简历结构化解析结果】")
        print(json.dumps(filtered_struct, ensure_ascii=False, indent=2)) 