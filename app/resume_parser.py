from app.llm import call_gpt
import os

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt", "resume_parser_prompt.txt")

def parse_resume(resume_text):
    """调用 LLM 对简历进行结构化解析，返回结构化字段。"""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        system_prompt = f.read()
    full_prompt = f"{system_prompt}\n\n简历/经历:\n{resume_text.strip()}"
    result = call_gpt(full_prompt)
    return result

if __name__ == "__main__":
    resume_text = '''
美籍华人，拥有中国永居身份，入选国家级人才计划，双学士，双硕士，博士。上交本科，佐治亚理工学院电子与计算机工程博士（美国三大理工学院之一，专业排名全美第二）。10多年美国工业界工作经验，专注于深度学习算法、软件框架、NPU芯片设计，拥有80+国际专利，20+顶会论文。
21年回国加入华为，现任ICT某产品线AI首席专家，21级。负责产品线AI Infra建设以及AI产品的研发和落地。
1. 在英伟达期间，作为高级总监，负责视频流分析平台Deepstream和迁移学习工具库TAO，并开始构建面向无人驾驶的主动学习数据引擎。
2. 在三星美国研究院期间，作为三星研究院最年轻的首席工程师，参与设计了三星猎户座处理器9810上的第一代移动NPU, 同时创建了三星虚拟训练数据引擎，使用3D渲染技术生成深度学习算法的训练数据，应用于目标识别，全景分割，深度，光流，HDR，超微光，超分辨率等计算机视觉应用。其中，所负责的虚拟景深项目长期霸占DXO Mark Mobile手机AI拍摄功能排行榜榜首位置。
3. 2013年创建TI嵌入式机器实验室，开发了工业界最早的嵌入式深度学习推理框架TIDL，设计了业内最早的车规级神经网络加速芯片MMA，应用于TI TDA4 ADAS SoC。

评价：
1 、软件与系统：精通高性能/高并发软件编程. 精通分布式系统与前沿数据库/大数据系统。
2 、A I：精通  Deep Learning 和现代大模型技术原理, 熟悉分布式训练, 高效LLM推理, RAG, Vector Database等技术 。
3 、芯片与硬件：熟悉数字/模拟 VLSI  电路, CPU 微架构, GPU 架构, DPU 架构, FPGA, 存内计算  原理 。了解 RDMA, CXL, PCIE, NVME  等协议. 。熟悉  EDA  设计流程及其建模技术 。熟悉半导体物 理原理.
4 、团队管理 ：8+年的团队管理经验, 具备从 0 到  1  的团队建设能力以及带领团队攻坚克难的能力， 现在带 600 人左右团队，包括大模型 、多模态 、硬件加速 、数据库等多种方向。

候选人简历
基本信息 
姓名：刘剑华
性别 ：男 年龄：42
目前所在地：上海

教育经历   
2005.09 - 2008.06 北京大学 微电子 硕士
2000.09 - 2004.06 北京大学 化学与分子工程 本科

工作经历
2021.10 – 至今        华为         首席软件专家/架构师（ 21）
职责业绩：
1 、面向私域ToB场景的端到端解决方案总架构师.  负责方向包括但不限于:
2 、自研高性能向量数据库加速 LLM 推理, Embedding, 多模态大模型, 推理硬件加速技术.
3 、异构芯片系统, 端到端加速   应用(利用  DPU, FPGA,  昇腾  GPU).
4 、以训推一体为中心的计算和存储架构(CXL, UB).
5 、存内计算(PIM)加速 LLM 训练和推理.

2012.12 – 2021.10         Microsoft（西雅图总部）    Principal Software Engineer Manager（ 66 ）
职责业绩：
1 、负责 Office 365  的  Meta Data Service,  服务于  Exchange Online, Teams ，SharePoint 后台 的,万租户, 32 亿用户.
2 、带领团队开发过 Teams, Exchange Online 两款重量级 Saas 云服务里面的超大规模元数据系  统以及部分 A I 系统. 涉及到的技术包括大型分布式系统的高可靠与高并发, 纯内存 SQL 数据库, 分 布式 CosmosDB 数据库, EventHub  中间件, Rest API, Deep Learning 等.  具有良好的跨团队, 跨 产品开发规划与领导力.

2008.06 – 2012.04        Synopsys 新思科技（ EDA 软件提供商）         Senopr R&D Engineer
职责业绩：
1 、负责 Synopsys 软件 ICC(ICCompiler)的后端布局与布线设计, 工艺优化(DFM)等,
2 、负责 EDA 流程前端大规模集成电路验证与仿真.涉及到凸优化,大型稀疏矩阵求解,特征值与特征向 量求解, 线性规划算法等数值计算与优化技术.
'''
    result = parse_resume(resume_text)
    print(result) 