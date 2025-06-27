# HuntingAIJob

基于大模型的智能人才匹配系统。支持解析岗位 JD 和候选人简历，结合结构化筛选与向量匹配，从数据库/向量数据库中高效筛选多位匹配候选人。

## 目录结构

```
HuntingAIJob/
├── app/                         # 主应用逻辑（后端服务 + 模型接口）
│   ├── main.py                  # Gradio 主程序入口
│   ├── gradio_ui.py             # Gradio 界面构建模块
│   ├── jd_parser.py             # JD 结构化模块（调用 LLM）
│   ├── resume_parser.py         # 简历结构化模块（调用 LLM）
│   ├── embedder.py              # 向量化模块（调用 embedding API）
│   ├── vector_store.py          # Chroma/FAISS 向量索引管理模块
│   ├── db.py                    # SQLite 数据库操作模块
│   ├── config.py                # API Key、路径、阈值、Top-N 等配置
│   └── ...
│
├── data/                        # 数据存储目录
│   ├── uploads/                 # 原始简历上传区
│   ├── chroma_db/               # Chroma 向量数据库文件
│   └── ...
│
├── logs/                        # 日志和任务文件
│   └── tasks.json               # 批量导入任务状态
│
├── prompt/                      # LLM 提示词模板
│   ├── jd_parser_prompt.txt
│   └── resume_parser_prompt.txt
│
├── run.py                       # 启动 Gradio 应用（入口）
├── requirements.txt
├── daemon_process.ps1            # PowerShell 守护进程脚本
├── batch_import_task.ps1         # 批量导入任务管理脚本
└── README.md
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API Key 和环境
- 编辑 `app/config.py`，填写你的 LLM API Key（如 OpenAI、DashScope 等）、embedding 模型等参数。
- 如需用环境变量配置 API Key，请在命令行或系统环境中设置。

### 3. 初始化数据库（如有需要）
如果有数据库初始化脚本（如 `scripts/init_db.py`）：
```bash
python scripts/init_db.py
```

### 4. 启动应用
```bash
python run.py
```
或以守护进程方式后台运行（推荐生产环境，Windows PowerShell）：
```powershell
./daemon_process.ps1 start
```
查看状态：
```powershell
./daemon_process.ps1 status
```
停止守护进程：
```powershell
./daemon_process.ps1 stop
```

### 5. 访问 Web UI
在浏览器中打开：
```
http://127.0.0.1:7860
```

### 6. 批量导入候选人
- 支持通过脚本或 Web UI 批量导入 Excel/简历。
- 批量导入任务管理（列出/取消/删除任务）：
```powershell
./batch_import_task.ps1 list
./batch_import_task.ps1 cancel <任务ID>
./batch_import_task.ps1 delete <任务ID>
./batch_import_task.ps1 help
```

## 主要依赖
- gradio
- openai / dashscope / 其他 LLM API
- chromadb / faiss
- sqlite3
- pandas

## 功能亮点
- 支持批量导入候选人简历，自动结构化并向量化入库
- 支持岗位 JD 智能解析与多维度匹配
- 支持 Gradio Web UI 交互
- 支持批量导入任务管理
- 支持守护进程后台运行，适合生产部署

---

如需详细说明，请参考代码注释及各脚本 docstring。 