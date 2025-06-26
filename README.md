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
│   ├── matcher.py               # 匹配逻辑（结构化筛选 + 向量匹配）
│   ├── db.py                    # SQLite 数据库操作模块
│   ├── vector_store.py          # FAISS 向量索引管理模块
│   └── config.py                # API Key、路径、阈值、Top-N 等配置
│
├── data/                        # 数据存储目录
│   ├── uploads/                 # 原始简历上传区
│   ├── candidate_vectors.index  # FAISS 向量索引文件
│   └── candidates.db            # SQLite 数据库存储结构化字段
│
├── scripts/                     # 辅助脚本
│   ├── init_db.py               # 初始化 SQLite 数据表
│   └── batch_import.py          # 批量导入已有 Excel / 简历的脚本
│
├── run.py                       # 启动 Gradio 应用（入口）
├── requirements.txt
└── README.md
```

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 初始化数据库：
   ```bash
   python scripts/init_db.py
   ```
3. 启动应用：
   ```bash
   python run.py
   ```

## 主要依赖
- gradio
- openai / dashscope / 其他 LLM API
- faiss
- sqlite3
- pandas

## 说明
- 支持批量导入候选人简历，自动结构化并向量化入库。
- 支持岗位 JD 智能解析与多维度匹配。
- 支持 Gradio Web UI 交互。 