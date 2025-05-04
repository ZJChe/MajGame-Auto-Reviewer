from nonebot import on_command, on_message
from nonebot.rule import to_me, startswith
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Event, Bot, Message

from .get_mspt import get_majsoul_pt
from .get_thpt import get_tenhou_pt

mspt = on_message(rule=startswith("mspt"), priority=10)
thpt = on_message(rule=startswith("thpt"), priority=10)

@mspt.handle()
async def handle_function(bot: Bot, event: Event):
    message = event.get_message().extract_plain_text()
    nickname = message[4:].strip()
    pt_result = get_majsoul_pt(nickname)
    await mspt.finish(f"{pt_result}")

@thpt.handle()
async def handle_function(bot: Bot, event: Event):
    message = event.get_message().extract_plain_text()
    nickname = message[4:].strip()
    pt_result = get_tenhou_pt(nickname)
    await mspt.finish(f"{pt_result}")