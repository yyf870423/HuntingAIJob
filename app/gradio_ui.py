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
    "天津": ["天津"],
    "上海": ["上海"],
    "重庆": ["重庆"],
    "河北": ["石家庄", "唐山", "秦皇岛", "邯郸", "邢台", "保定", "张家口", "承德", "沧州", "廊坊", "衡水"],
    "山西": ["太原", "大同", "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "忻州", "临汾", "吕梁"],
    "辽宁": ["沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛"],
    "吉林": ["长春", "吉林", "四平", "辽源", "通化", "白山", "松原", "白城", "延边朝鲜族自治州"],
    "黑龙江": ["哈尔滨", "齐齐哈尔", "鸡西", "鹤岗", "双鸭山", "大庆", "伊春", "佳木斯", "七台河", "牡丹江", "黑河", "绥化", "大兴安岭地区"],
    "江苏": ["南京", "无锡", "徐州", "常州", "苏州", "南通", "连云港", "淮安", "盐城", "扬州", "镇江", "泰州", "宿迁"],
    "浙江": ["杭州", "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水"],
    "安徽": ["合肥", "芜湖", "蚌埠", "淮南", "马鞍山", "淮北", "铜陵", "安庆", "黄山", "滁州", "阜阳", "宿州", "巢湖", "六安", "亳州", "池州", "宣城"],
    "福建": ["福州", "厦门", "莆田", "三明", "泉州", "漳州", "南平", "龙岩", "宁德"],
    "江西": ["南昌", "景德镇", "萍乡", "九江", "新余", "鹰潭", "赣州", "吉安", "宜春", "抚州", "上饶"],
    "山东": ["济南", "青岛", "淄博", "枣庄", "东营", "烟台", "潍坊", "济宁", "泰安", "威海", "日照", "莱芜", "临沂", "德州", "聊城", "滨州", "菏泽"],
    "河南": ["郑州", "开封", "洛阳", "平顶山", "安阳", "鹤壁", "新乡", "焦作", "濮阳", "许昌", "漯河", "三门峡", "南阳", "商丘", "信阳", "周口", "驻马店", "济源"],
    "湖北": ["武汉", "黄石", "十堰", "宜昌", "襄阳", "鄂州", "荆门", "孝感", "荆州", "黄冈", "咸宁", "随州", "恩施土家族苗族自治州", "仙桃", "潜江", "天门", "神农架林区"],
    "湖南": ["长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德", "张家界", "益阳", "郴州", "永州", "怀化", "娄底", "湘西土家族苗族自治州"],
    "广东": ["广州", "韶关", "深圳", "珠海", "汕头", "佛山", "江门", "湛江", "茂名", "肇庆", "惠州", "梅州", "汕尾", "河源", "阳江", "清远", "东莞", "中山", "潮州", "揭阳", "云浮"],
    "广西": ["南宁", "柳州", "桂林", "梧州", "北海", "防城港", "钦州", "贵港", "玉林", "百色", "贺州", "河池", "来宾", "崇左"],
    "海南": ["海口", "三亚", "三沙", "儋州", "五指山", "琼海", "文昌", "万宁", "东方", "定安县", "屯昌县", "澄迈县", "临高县", "白沙黎族自治县", "昌江黎族自治县", "乐东黎族自治县", "陵水黎族自治县", "保亭黎族苗族自治县", "琼中黎族苗族自治县"],
    "四川": ["成都", "自贡", "攀枝花", "泸州", "德阳", "绵阳", "广元", "遂宁", "内江", "乐山", "南充", "眉山", "宜宾", "广安", "达州", "雅安", "巴中", "资阳", "阿坝藏族羌族自治州", "甘孜藏族自治州", "凉山彝族自治州"],
    "贵州": ["贵阳", "六盘水", "遵义", "安顺", "毕节", "铜仁", "黔西南布依族苗族自治州", "黔东南苗族侗族自治州", "黔南布依族苗族自治州"],
    "云南": ["昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧", "楚雄彝族自治州", "红河哈尼族彝族自治州", "文山壮族苗族自治州", "西双版纳傣族自治州", "大理白族自治州", "德宏傣族景颇族自治州", "怒江傈僳族自治州", "迪庆藏族自治州"],
    "西藏": ["拉萨", "日喀则", "昌都", "林芝", "山南", "那曲", "阿里"],
    "陕西": ["西安", "铜川", "宝鸡", "咸阳", "渭南", "延安", "汉中", "榆林", "安康", "商洛"],
    "甘肃": ["兰州", "嘉峪关", "金昌", "白银", "天水", "武威", "张掖", "平凉", "酒泉", "庆阳", "定西", "陇南", "临夏回族自治州", "甘南藏族自治州"],
    "青海": ["西宁", "海东", "海北藏族自治州", "黄南藏族自治州", "海南藏族自治州", "果洛藏族自治州", "玉树藏族自治州", "海西蒙古族藏族自治州"],
    "宁夏": ["银川", "石嘴山", "吴忠", "固原", "中卫"],
    "新疆": ["乌鲁木齐", "克拉玛依", "吐鲁番", "哈密", "昌吉回族自治州", "博尔塔拉蒙古自治州", "巴音郭楞蒙古自治州", "阿克苏地区", "克孜勒苏柯尔克孜自治州", "喀什地区", "和田地区", "伊犁哈萨克自治州", "塔城地区", "阿勒泰地区", "石河子", "阿拉尔", "图木舒克", "五家渠", "北屯", "铁门关", "双河", "可克达拉", "昆玉", "胡杨河"],
    "香港": ["香港"],
    "澳门": ["澳门"],
    "台湾": ["台北", "高雄", "台中", "台南", "新北", "基隆", "新竹", "嘉义", "桃园", "彰化", "屏东", "南投", "云林", "宜兰", "花莲", "台东", "澎湖", "金门", "连江"]
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