import threading
import uuid
import time
import json
import os
from app.batch_import import parse_excel_file

tasks_file = os.path.join(os.path.dirname(__file__), '../logs/tasks.json')

def load_tasks():
    if not os.path.exists(tasks_file):
        return {}
    with open(tasks_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_tasks(tasks):
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def batch_import_task(task_id, file_path):
    tasks = load_tasks()
    tasks[task_id]["status"] = "running"
    tasks[task_id]["start_time"] = time.time()
    save_tasks(tasks)
    try:
        count = parse_excel_file(file_path, task_id=task_id)
        tasks = load_tasks()
        if tasks[task_id].get("cancel"):
            tasks[task_id]["status"] = "cancelled"
            tasks[task_id]["result"] = "任务已取消"
        else:
            tasks[task_id]["status"] = "finished"
            tasks[task_id]["result"] = f"导入完成，共{count}条"
        tasks[task_id]["end_time"] = time.time()
        save_tasks(tasks)
    except Exception as e:
        tasks = load_tasks()
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["end_time"] = time.time()
        tasks[task_id]["result"] = f"失败: {e}"
        save_tasks(tasks)

def start_batch_import(file_path):
    task_id = str(uuid.uuid4())
    tasks = load_tasks()
    tasks[task_id] = {"status": "pending", "file": file_path, "cancel": False}
    save_tasks(tasks)
    t = threading.Thread(target=batch_import_task, args=(task_id, file_path))
    t.start()
    return task_id

def get_all_tasks():
    tasks = load_tasks()
    return {tid: {k: v for k, v in info.items()} for tid, info in tasks.items()}

def cancel_task(task_id):
    tasks = load_tasks()
    if task_id in tasks and tasks[task_id]["status"] == "running":
        tasks[task_id]["cancel"] = True
        save_tasks(tasks)
        return True
    return False 