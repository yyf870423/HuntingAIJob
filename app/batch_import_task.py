import json
import sys
import os
import time

TASKS_FILE = os.path.join(os.path.dirname(__file__), '../logs/tasks.json')

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {}
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def cancel_task(task_id):
    tasks = load_tasks()
    if task_id in tasks and tasks[task_id].get('status') == 'running':
        tasks[task_id]['cancel'] = True
        save_tasks(tasks)
        print(f"任务 {task_id} 已请求取消。"); return True
    else:
        print(f"任务 {task_id} 不存在或不在运行中。"); return False

def delete_task(task_id):
    tasks = load_tasks()
    if task_id in tasks:
        del tasks[task_id]
        save_tasks(tasks)
        print(f"任务 {task_id} 已删除。"); return True
    else:
        print(f"任务 {task_id} 不存在。"); return False

def list_tasks():
    tasks = load_tasks()
    print(f"{'任务ID':36}  {'状态':8}  {'开始时间':19}  {'结束时间':19}  结果")
    print('-'*100)
    for tid, info in tasks.items():
        status = info.get('status', '')
        def format_time(ts):
            if not ts:
                return ''
            import datetime
            return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        start_time = format_time(info.get('start_time', 0))
        end_time = format_time(info.get('end_time', 0))
        result = info.get('result', '')
        print(f"{tid:36}  {status:8}  {start_time:19}  {end_time:19}  {result}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python batch_import_task.py [list|cancel|delete] [任务ID]")
        sys.exit(1)
    action = sys.argv[1]
    if action == 'cancel' and len(sys.argv) >= 3:
        cancel_task(sys.argv[2])
    elif action == 'delete' and len(sys.argv) >= 3:
        delete_task(sys.argv[2])
    elif action == 'list':
        list_tasks()
    else:
        print("未知操作，只支持 list、cancel 或 delete") 