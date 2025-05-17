import os
from typing import Annotated
from urllib.parse import urlparse

from nonebot import on_command, on_message, on_shell_command
from nonebot.rule import to_me, startswith, shell_command, ArgumentParser, Namespace
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.adapters.onebot.v11 import Event, Bot, Message
from nonebot.exception import ParserExit, FinishedException
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .get_setu import get_setu_lilicon

parser = ArgumentParser()
parser.add_argument("-r", "--r18", action="store_true", default=False)
parser.add_argument("-t", "--tag", default=None)

setu = on_shell_command("setu", aliases={"色图"}, priority=10, block=True, parser=parser)


@setu.handle()
async def handle_setu(foo: Annotated[ParserExit, ShellCommandArgs()]):
    if foo.status == 0:
        await setu.finish(foo.message)  # help message
    else:
        await setu.finish(foo.message)  # error message

@setu.handle()
async def handle_setu(foo: Annotated[Namespace, ShellCommandArgs()]):
    arg_dict = vars(foo)
    r18 = arg_dict.get("r18")
    tag = arg_dict.get("tag")
    local_path = None

    try:
        local_path = await get_setu_lilicon(r18, tag)

        if os.path.exists(local_path):
            # 先发，再删
            await setu.send(MessageSegment.image(file=local_path))
            os.remove(local_path)
            await setu.finish()
        else:
            await setu.finish(f"出错：{local_path}")
    except FinishedException:
        raise
    except Exception as e:
        logger.error(f"发生错误: {e}, url: {local_path}")
        # 出错时也尝试清理
        if local_path and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception as del_err:
                logger.warning(f"清理失败: {del_err}")
        await setu.finish(f"发生错误,请检查API是否正常。\n{local_path}")
