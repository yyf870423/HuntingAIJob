import gradio as gr
from app.vector_store import collection
import time
from app.jd_parser import parse_jd
from app.vector_store import get_embedding_from_llm, query_candidates
from app.logger import logger

# 省市二级列表（示例，实际可补充更多）
PROVINCES_CITIES = {
    "北京": ["北京"],
    "上海": ["上海"],
    "广东": ["广州", "深圳", "珠海", "佛山"],
    "江苏": ["南京", "苏州", "无锡", "常州"],
    "浙江": ["杭州", "宁波", "温州"],
    "四川": ["成都", "绵阳"],
    "重庆": ["重庆"],
    "山东": ["济南", "青岛"],
    "湖北": ["武汉"],
    "湖南": ["长沙"],
    # ... 可补充更多
}

# 学历选项
DEGREE_OPTIONS = ["本科及以上", "硕士及以上", "博士"]

# 获取行业选项（从Chroma数据库元数据中去重获取"行业"字段）
def get_industry_options():
    # 获取所有元数据
    all_metas = collection.get()["metadatas"]
    industries = set()
    for meta in all_metas:
        if meta and "行业" in meta and meta["行业"]:
            industries.add(meta["行业"])
    return sorted(list(industries))


def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## 智能人才匹配系统")
        with gr.Tab("上传简历"):
            # 这里后续添加上传简历的内容
            pass
        with gr.Tab("搜索候选人"):
            with gr.Row():
                # 左侧：筛选条件、岗位描述、结果控制
                with gr.Column(scale=2):
                    gr.Markdown("### 筛选条件")
                    # 第一行：行业、学历
                    with gr.Row():
                        industry_options = get_industry_options()
                        industry_options = ["全部"] + industry_options
                        industry = gr.Dropdown(
                            choices=industry_options,
                            label="行业",
                            value="全部",
                            interactive=True
                        )
                        degree_options = ["全部"] + DEGREE_OPTIONS
                        degree = gr.Dropdown(
                            choices=degree_options,
                            label="学历",
                            value="全部",
                            interactive=True
                        )
                    # 第二行：省份、城市
                    with gr.Row():
                        province_options = ["全部"] + list(PROVINCES_CITIES.keys())
                        province = gr.Dropdown(
                            choices=province_options,
                            label="省份",
                            value="全部",
                            interactive=True
                        )
                        city = gr.Dropdown(
                            choices=["全部"],
                            label="城市（请选择）",
                            value="全部",
                            allow_custom_value=True,
                            interactive=True
                        )

                    def update_cities(selected_province):
                        if selected_province and selected_province != "全部" and selected_province in PROVINCES_CITIES:
                            city_choices = ["全部"] + [str(city) for city in PROVINCES_CITIES[selected_province]]
                        else:
                            city_choices = ["全部"]
                        return gr.Dropdown(
                            choices=city_choices,
                            value="全部",
                            label="城市（请选择）",
                            allow_custom_value=True,
                            interactive=True
                        )
                    province.change(update_cities, inputs=province, outputs=city)

                    gr.Markdown("### 岗位描述")
                    jd_text = gr.TextArea(
                        label="请输入岗位JD描述（必填）",
                        placeholder="请粘贴或输入岗位描述...",
                        lines=8,
                        max_lines=20,
                        interactive=True
                    )

                    gr.Markdown("### 结果控制")
                    with gr.Column():
                        similarity = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.2,
                            step=0.01,
                            label="相似度"
                        )
                        top_k = gr.Slider(
                            minimum=1,
                            maximum=100,
                            value=30,
                            step=1,
                            label="返回 Top 数量"
                        )
                    # 这里可添加搜索按钮等
                    match_btn = gr.Button("开始匹配", elem_id="match-btn")

                # 右侧：候选人列表展示
                with gr.Column(scale=5):
                    candidates_md = gr.Markdown(
                        value="请在左侧填写筛选条件并点击搜索。",  # 初始占位内容
                        visible=True,  # 始终可见
                        label="筛选结果"
                    )

                    def do_match(industry_val, degree_val, province_val, city_val, jd_val, similarity_val, topk_val):
                        logger.info(f"[UI] 开始匹配: 行业={industry_val}, 学历={degree_val}, 省份={province_val}, 城市={city_val}, JD={jd_val[:30]}..., 相似度={similarity_val}, top_k={topk_val}")
                        print(f"[UI] 开始匹配: 行业={industry_val}, 学历={degree_val}, 省份={province_val}, 城市={city_val}, JD={jd_val[:30]}..., 相似度={similarity_val}, top_k={topk_val}")
                        t0 = time.time()
                        # 1. 解析JD
                        try:
                            jd_struct = parse_jd(jd_val)
                            logger.info(f"[JD解析] 结构化结果: {jd_struct}")
                            print(f"[JD解析] 结构化结果: {jd_struct}")
                        except Exception as e:
                            logger.error(f"JD解析失败: {e}")
                            return "JD解析失败，请检查输入。"
                        # 2. 向量化JD
                        try:
                            jd_emb = get_embedding_from_llm(jd_val)
                        except Exception as e:
                            logger.error(f"JD向量化失败: {e}")
                            return "JD向量化失败，请检查输入。"
                        # 3. 构造where条件
                        where = {}
                        if industry_val and industry_val != "全部":
                            where["行业"] = industry_val
                        if degree_val and degree_val != "全部":
                            where["学历"] = degree_val
                        if city_val and city_val != "全部":
                            where["位置"] = city_val
                        logger.info(f"[检索] where条件: {where}")
                        print(f"[检索] where条件: {where}")
                        # 4. 检索
                        try:
                            if where:
                                result = query_candidates(jd_emb, n_results=topk_val, where=where)
                            else:
                                result = query_candidates(jd_emb, n_results=topk_val)
                        except Exception as e:
                            logger.error(f"候选人检索失败: {e}")
                            return "候选人检索失败，请检查后端服务。"
                        metadatas = result.get('metadatas', [[]])[0]
                        logger.info(f"[检索] 返回候选人数: {len(metadatas)}")
                        print(f"[检索] 返回候选人数: {len(metadatas)}")
                        # 5. 格式化为HTML表格，部分列nowrap
                        headers = ["姓名", "行业", "类别", "在职公司", "性别", "年龄", "学历", "学校", "专业", "位置", "手机号", "邮箱"]
                        nowrap_cols = {"姓名", "行业", "位置", "手机号", "邮箱", "学历"}
                        html = "<div style='overflow-x:auto;'><table border='1' style='border-collapse:collapse;width:100%;'>"
                        html += "<thead><tr>" + "".join(f"<th style='white-space:nowrap;'>{h}</th>" for h in headers) + "</tr></thead><tbody>"
                        for meta in metadatas:
                            html += "<tr>"
                            for h in headers:
                                val = str(meta.get(h, "")).replace("\n", " ").replace("\r", " ")
                                if h in nowrap_cols:
                                    html += f"<td style='white-space:nowrap;'>{val}</td>"
                                else:
                                    html += f"<td>{val}</td>"
                            html += "</tr>"
                        html += "</tbody></table></div>"
                        t1 = time.time()
                        html += f"<div style='margin-top:8px;color:#888;'>本次筛选耗时 {t1-t0:.2f} 秒，共 {len(metadatas)} 人</div>"
                        return html

                    match_btn.click(
                        do_match,
                        inputs=[industry, degree, province, city, jd_text, similarity, top_k],
                        outputs=candidates_md
                    )

    # 已回滚右侧滚动条和自适应高度

    return demo 