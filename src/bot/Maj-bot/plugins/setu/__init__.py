from typing import Annotated

from nonebot import on_command, on_message, on_shell_command
from nonebot.rule import to_me, startswith, shell_command, ArgumentParser, Namespace
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.adapters.onebot.v11 import Event, Bot, Message
from nonebot.exception import ParserExit
from nonebot import logger

from .get_setu import get_setu_lilicon

parser = ArgumentParser()
parser.add_argument("-r", "--r18", action="store_true", default=False)
parser.add_argument("-t", "--tag", default=None)

setu = on_shell_command("setu", aliases={"色图"}, priority=10, block=True, parser=parser)

@setu.handle()
async def handle_setu(foo: Annotated[ParserExit, ShellCommandArgs()]):
    if foo.status == 0:
        setu.finish(foo.message)  # help message
    else:
        setu.finish(foo.message)  # error message

@setu.handle()
async def handle_setu(foo: Annotated[Namespace, ShellCommandArgs()]):
    arg_dict = vars(foo)
    r18 = arg_dict.get("r18")
    tag = arg_dict.get("tag")
    url = get_setu_lilicon(False, tag)
    await setu.finish(Message(f'[CQ:image,file={url}]'))
    