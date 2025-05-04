from nonebot import on_command, on_message
from nonebot.rule import to_me, startswith
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event, Bot, Message
import asyncio

import subprocess

restart = on_command("re", rule=to_me(), priority=10, block=True)

admins = ['1548999469', '3263919697']

@restart.handle()
async def handle_function(bot: Bot, event: Event):
    if event.get_user_id() not in admins:
        await restart.finish("你没有权限使用这个命令！")
    else:
        await restart.send("重启中")

        await asyncio.sleep(1)

        subprocess.Popen(["/bin/bash", "/home/cyc/MajGame-Auto-Reviewer/src/bot/restart.sh"])
            

