# 安装与运行指南

本项目为基于大语言模型的人才匹配系统，后端为 Python，前端为 Gradio UI。以下为详细的安装与运行步骤。

## 1. 安装 Python 3.11.9

1. 访问 [Python 官网](https://www.python.org/downloads/release/python-3119/) 下载适用于 Windows 的 Python 3.11.9 安装包。
2. 安装时请勾选 "Add Python to PATH"。
3. 安装完成后，打开 PowerShell，输入以下命令检查 Python 是否安装成功：

   ```powershell
   python --version
   ```
   
   输出应为：
   ```
   Python 3.11.9
   ```

## 2. 配置 OpenAI API Key

1. 打开项目根目录下的 `config.json` 文件。
2. 将你的 OpenAI API Key 填入 `OPENAI_API_KEY` 字段。例如：
   ```json
   {
     "OPENAI_API_KEY": "sk-xxxxxx...",
     // 其他配置项
   }
   ```
3. 保存文件。

## 3. 在 PowerShell 中运行 daemon_process.ps1

1. 打开 PowerShell，进入项目根目录（假设为 `D:\Software\ai_project\HuntingAIJob`）：
   ```powershell
   cd D:\Software\ai_project\HuntingAIJob
   ```
2. 启动后端服务（首次运行会自动创建虚拟环境并安装依赖）：
   ```powershell
   .\daemon_process.ps1 start
   ```
   - 启动后会在后台运行 `run.py`，并记录进程号到 `daemon_process.pid`。
3. 查看服务状态：
   ```powershell
   .\daemon_process.ps1 status
   ```
4. 停止服务：
   ```powershell
   .\daemon_process.ps1 stop
   ```
5. 查看帮助：
   ```powershell
   .\daemon_process.ps1 help
   ```

## 4. 在 PowerShell 中使用 batch_import_task.ps1

1. 进入项目根目录：
   ```powershell
   cd D:\Software\ai_project\HuntingAIJob
   ```
2. 查看所有批量导入任务：
   ```powershell
   .\batch_import_task.ps1 list
   ```
3. 取消指定任务（以 TaskID 为例）：
   ```powershell
   .\batch_import_task.ps1 cancel <TaskID>
   ```
4. 删除指定任务（以 TaskID 为例）：
   ```powershell
   .\batch_import_task.ps1 delete <TaskID>
   ```
5. 查看帮助：
   ```powershell
   .\batch_import_task.ps1 help
   ```

---
如有问题请先确认 Python 版本与依赖环境，或查阅 README.md 获取更多信息。 