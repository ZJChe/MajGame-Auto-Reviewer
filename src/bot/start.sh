#!/bin/bash

# 激活 Conda 环境
source ~/miniconda3/etc/profile.d/conda.sh  # 或者你自己 Conda 安装路径
conda activate nonebot

# 启动 bot.py，输出日志到 nohup.out
nohup python bot.py > nonebot.log 2>&1 &

# 保存进程号
echo $! > bot_pid.log
echo "Bot started with PID $(cat bot_pid.log)"
