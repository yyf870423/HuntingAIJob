#!/bin/bash

show_help() {
    echo "Usage:"
    echo "  ./batch_import_task.sh list                 # List all tasks"
    echo "  ./batch_import_task.sh cancel <TaskID>      # Cancel the specified task"
    echo "  ./batch_import_task.sh delete <TaskID>      # Delete the specified task"
    echo "  ./batch_import_task.sh help                 # Show this help message"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/app/batch_import_task.py"

ACTION=$1
TASK_ID=$2

case "$ACTION" in
    list)
        python3 "$PYTHON_SCRIPT" list
        ;;
    cancel)
        if [ -n "$TASK_ID" ]; then
            python3 "$PYTHON_SCRIPT" cancel "$TASK_ID"
        else
            show_help
            exit 1
        fi
        ;;
    delete)
        if [ -n "$TASK_ID" ]; then
            python3 "$PYTHON_SCRIPT" delete "$TASK_ID"
        else
            show_help
            exit 1
        fi
        ;;
    help)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac 