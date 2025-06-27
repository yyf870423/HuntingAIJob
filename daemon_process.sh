#!/bin/bash
# Usage:
#   ./daemon_process.sh start   # Start run.py as a daemon process, record PID to daemon_process.pid
#   ./daemon_process.sh status  # Check if the process exists, return PID if running
#   ./daemon_process.sh stop    # Stop the daemon process
#   ./daemon_process.sh help    # Show help

PID_FILE="daemon_process.pid"

show_help() {
    echo "Usage:"
    echo "  ./daemon_process.sh start   # Start run.py as a daemon process, record PID to daemon_process.pid"
    echo "  ./daemon_process.sh status  # Check if the process exists, return PID if running"
    echo "  ./daemon_process.sh stop    # Stop the daemon process"
    echo "  ./daemon_process.sh help    # Show help"
}

start_runpy() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo "run.py is already running, PID: $pid"
            return
        else
            rm -f "$PID_FILE"
        fi
    fi
    nohup python3 run.py > run.log 2>&1 &
    echo $! > "$PID_FILE"
    echo "run.py started as a daemon process, PID: $(cat $PID_FILE), written to $PID_FILE"
}

status_runpy() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            echo "run.py is running, PID: $pid"
        else
            echo "run.py is not running (pid file exists but process does not)"
        fi
    else
        echo "run.py is not running (no pid file)"
    fi
}

stop_runpy() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            kill $pid
            echo "Stopped run.py daemon process (PID: $pid)"
        else
            echo "Process PID $pid does not exist, nothing to stop."
        fi
        rm -f "$PID_FILE"
    else
        echo "No pid file found, nothing to stop."
    fi
}

case "$1" in
    start)
        start_runpy
        ;;
    status)
        status_runpy
        ;;
    stop)
        stop_runpy
        ;;
    help)
        show_help
        ;;
    *)
        show_help
        ;;
esac 