import gradio as gr
from app.vector_store import collection
import time
from app.jd_parser import parse_jd
from app.vector_store import get_embedding_from_llm, query_candidates
from app.logger import logger
from gradio import Warning
from app.resume_parser import parse_resume
from app.vector_store import add_candidate
import gradio as gradio_mod
from app.batch_import import parse_excel_file
from app.single_import import single_import
from app.batch_import_async import start_batch_import, get_all_tasks, cancel_task
import shutil
import os

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
                        province_options = ["请选择省份"] + list(PROVINCES_CITIES.keys())
                        province = gr.Dropdown(
                            choices=province_options,
                            label="省份",
                            value="请选择省份",
                            allow_custom_value=True,
                            interactive=True
                        )
                        city = gr.Dropdown(
                            choices=["请选择城市"],
                            label="城市",
                            value="请选择城市",
                            allow_custom_value=True,
                            interactive=True
                        )

                    def update_cities(selected_province):
                        if selected_province and selected_province != "请选择省份" and selected_province in PROVINCES_CITIES:
                            city_choices = ["请选择城市"] + [str(city) for city in PROVINCES_CITIES[selected_province]]
                        else:
                            city_choices = ["请选择城市"]
                        return gr.Dropdown(
                            choices=city_choices,
                            value="请选择城市",
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
                            value=0.75,
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
                        t0 = time.time()
                        # 1. 解析JD
                        try:
                            jd_struct = parse_jd(jd_val)
                            logger.info(f"[JD解析] 结构化结果: {jd_struct}")
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
                        # 学历多值映射
                        if degree_val and degree_val != "全部":
                            if degree_val == "本科及以上":
                                where["学历"] = {"$in": ["本科", "硕士", "博士"]}
                            elif degree_val == "硕士及以上":
                                where["学历"] = {"$in": ["硕士", "博士"]}
                            else:
                                where["学历"] = degree_val
                        # 城市条件过滤
                        if city_val and city_val != "全部" and city_val != "请选择城市":
                            where["位置"] = city_val
                        logger.info(f"[检索] where条件: {where}")
                        # 4. 检索
                        try:
                            if where:
                                result = query_candidates(jd_emb, n_results=topk_val, where=where, similarity_threshold=similarity_val)
                            else:
                                result = query_candidates(jd_emb, n_results=topk_val, similarity_threshold=similarity_val)
                        except Exception as e:
                            logger.error(f"候选人检索失败: {e}")
                            return "候选人检索失败，请检查后端服务。"
                        metadatas = result.get('metadatas', [[]])[0]
                        distances = result.get('distances', [[]])[0]
                        logger.info(f"[检索] 返回候选人数: {len(metadatas)}")
                        # 5. 格式化为HTML表格，部分列nowrap
                        headers = ["姓名", "行业", "类别", "在职公司", "性别", "年龄", "学历", "学校", "专业", "位置", "手机号", "邮箱", "相似度"]
                        nowrap_cols = {"姓名", "行业", "位置", "手机号", "邮箱", "学历", "相似度"}
                        html = "<div style='overflow-x:auto;'><table border='1' style='border-collapse:collapse;width:100%;'>"
                        html += "<thead><tr>" + "".join(f"<th style='white-space:nowrap;'>{h}</th>" for h in headers) + "</tr></thead><tbody>"
                        for meta, dist in zip(metadatas, distances):
                            sim = 1 - dist
                            html += "<tr>"
                            for h in headers[:-1]:
                                val = str(meta.get(h, "")).replace("\n", " ").replace("\r", " ")
                                if h in nowrap_cols:
                                    html += f"<td style='white-space:nowrap;'>{val}</td>"
                                else:
                                    html += f"<td>{val}</td>"
                            html += f"<td style='white-space:nowrap;'>{sim:.4f}</td>"
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
        with gr.Tab("上传简历"):
            with gr.Column():
                upload_mode_radio = gr.Radio(
                    choices=["单个上传", "批量上传"],
                    value="单个上传",
                    label="上传方式"
                )
                # 单个上传模式下的表单字段
                single_fields = [
                    ("姓名（必填）", "", "姓名"), ("性别（必填）", "", "性别"), ("行业（必填）", "", "行业"), ("年龄", "", "年龄"), ("类别", "", "类别"), ("在职公司", "", "在职公司"), ("现岗位", "", "现岗位"),
                    ("学历", "", "学历"), ("学校", "", "学校"), ("专业", "", "专业"), ("手机号", "", "手机号"), ("邮箱", "", "邮箱")
                ]
                single_inputs = []
                # 第一行：姓名、性别、行业、年龄、类别、在职公司、现岗位
                with gr.Row():
                    for idx, (label, default, raw_label) in enumerate(single_fields[:7]):
                        if raw_label == "性别":
                            tb = gr.Dropdown(label=label, choices=["男", "女"], value=None, visible=True)
                        elif raw_label == "年龄":
                            tb = gr.Number(label=label, value=None, minimum=0, precision=0, visible=True)
                        else:
                            tb = gr.Textbox(label=label, value=default, visible=True)
                        single_inputs.append(tb)
                # 第二行：学历、学校、专业、手机号、邮箱、省份、城市
                with gr.Row():
                    # 学历
                    tb = gr.Dropdown(label=single_fields[7][0], choices=["本科", "硕士", "博士"], value=None, visible=True)
                    single_inputs.append(tb)
                    # 学校、专业、手机号
                    for label, default, raw_label in single_fields[8:11]:
                        tb = gr.Textbox(label=label, value=default, visible=True)
                        single_inputs.append(tb)
                    # 邮箱
                    email_box = gr.Textbox(label=single_fields[11][0], value=single_fields[11][1], visible=True)
                    single_inputs.append(email_box)
                    # 省份、城市
                    province_options = ["请选择省份"] + list(PROVINCES_CITIES.keys())
                    province_box = gr.Dropdown(label="省份", choices=province_options, value="请选择省份", visible=True)
                    city_box = gr.Dropdown(label="城市", choices=["请选择城市"], value="请选择城市", visible=True)
                # 省份-城市联动逻辑，参照"搜索候选人"tab
                def update_cities(selected_province):
                    if selected_province and selected_province != "请选择省份" and selected_province in PROVINCES_CITIES:
                        city_choices = ["请选择城市"] + [str(city) for city in PROVINCES_CITIES[selected_province]]
                    else:
                        city_choices = ["请选择城市"]
                    return gr.Dropdown(choices=city_choices, value="请选择城市", label="城市", interactive=True)
                province_box.change(update_cities, inputs=province_box, outputs=city_box)
                resume_text = gr.TextArea(label="简历/经历", lines=8, max_lines=15, visible=True)
                # 批量上传模式下的 xlsx 文件上传
                batch_upload = gr.File(
                    label="上传文件",
                    file_types=[".xlsx"],
                    visible=False,
                    interactive=True
                )
                def show_upload_mode(selected_mode):
                    if selected_mode == "单个上传":
                        return [gr.update(visible=True)] * (len(single_inputs) + 1) + [gr.update(visible=True)] * 2 + [gr.update(visible=False)]
                    else:
                        return [gr.update(visible=False)] * (len(single_inputs) + 1) + [gr.update(visible=False)] * 2 + [gr.update(visible=True)]
                upload_mode_radio.change(
                    show_upload_mode,
                    inputs=upload_mode_radio,
                    outputs=single_inputs + [resume_text, province_box, city_box, batch_upload]
                )
                status_md = gr.Markdown(visible=False)
                parse_btn = gr.Button("开始解析")
                def single_upload_logic(mode, *args):
                    if mode != "单个上传":
                        return "请切换到单个上传模式。", *args
                    values = args[:len(single_inputs)]
                    resume_val = args[len(single_inputs)]
                    province_val = args[len(single_inputs)+1]
                    city_val = args[len(single_inputs)+2]
                    meta_keys = [f[2] for f in single_fields]
                    metadata = {k: v for k, v in zip(meta_keys, values)}
                    metadata["位置"] = city_val if city_val and city_val != "请选择城市" else ""
                    metadata["经历"] = resume_val
                    try:
                        op_type, candidate_id = single_import(metadata)
                    except Exception as e:
                        return f"<span style='color:red'>上传失败: {e}</span>", *args
                    clear_vals = []
                    for comp in single_inputs:
                        if isinstance(comp, gr.Number):
                            clear_vals.append(None)
                        else:
                            clear_vals.append("")
                    clear_vals += [""] + ["请选择省份", "请选择城市", None]
                    return f"<span style='color:green'>{op_type}成功！</span>", *clear_vals
                # 新的回调：校验+解析+入库+清空
                parse_btn.click(
                    single_upload_logic,
                    inputs=[upload_mode_radio] + single_inputs + [resume_text, province_box, city_box, batch_upload],
                    outputs=[status_md] + single_inputs + [resume_text, province_box, city_box, batch_upload]
                )
                def batch_upload_logic(mode, *args):
                    if mode != "批量上传":
                        return "请切换到批量上传模式。", *args
                    file_obj = args[-1]
                    if file_obj is None:
                        return "<span style='color:red'>请上传xlsx文件！</span>", *args
                    # 保存到自定义目录 data/uploads
                    save_dir = os.path.join(os.path.dirname(__file__), '../data/uploads')
                    os.makedirs(save_dir, exist_ok=True)
                    filename = os.path.basename(file_obj.name)
                    new_path = os.path.abspath(os.path.join(save_dir, filename))
                    shutil.copy(file_obj.name, new_path)
                    # 直接用绝对路径传递
                    task_id = start_batch_import(new_path)
                    return f"<span style='color:green'>任务已开始执行，任务ID: {task_id}。请前往'批量任务管理'Tab查看进度。</span>", *args[:-1] + (None,)

                # 绑定批量上传逻辑
                parse_btn.click(
                    batch_upload_logic,
                    inputs=[upload_mode_radio] + single_inputs + [resume_text, province_box, city_box, batch_upload],
                    outputs=[status_md] + single_inputs + [resume_text, province_box, city_box, batch_upload]
                )

    # 已回滚右侧滚动条和自适应高度

    return demo 