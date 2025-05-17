from nonebot import on_command, on_message
from nonebot.rule import to_me, startswith
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event, Bot, Message
import asyncio
import subprocess
import os

restart = on_command("restart", priority=10, block=True)

admins = ['1548999469', '3263919697']

@restart.handle()
async def handle_function(bot: Bot, event: Event):
    if event.get_user_id() not in admins:
        await restart.finish("你没有权限使用这个命令！")
    else:
        await restart.send("重启中")

        await asyncio.sleep(1)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "bot", "restart.sh"))

        subprocess.Popen(["/bin/bash", script_path])
        