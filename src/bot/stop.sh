#!/bin/bash

if [ -f bot_pid.log ]; then
    PID=$(cat bot_pid.log)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "Bot with PID $PID stopped."
    else
        echo "No process with PID $PID is running."
    fi
    rm -f bot_pid.log
else
    echo "No bot_pid.log file found. Bot may not be running."
fi
