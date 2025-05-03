from nonebot import on_command
from nonebot.rule import to_me, startswith
from nonebot.params import CommandArg
from nonebot.adapters import Message

from .get_mspt import get_majsoul_pt

mspt = on_message(rule=startswith("mspt"), priority=10)

@mspt.handle()
async def handle_function(args: Message = CommandArg()):
    # 提取参数纯文本作为地名，并判断是否有效
    if nickname := args.extract_plain_text():
        pt_result = get_majsoul_pt(nickname)
        await mspt.finish(f"{pt_result}")
    else:
        await mspt.finish("请输入雀魂用户名")
