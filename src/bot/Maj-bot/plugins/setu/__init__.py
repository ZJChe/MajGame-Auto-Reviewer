from typing import Annotated
from urllib.parse import urlparse

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

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme in ['http', 'https', 'ftp'], result.netloc])
    except ValueError:
        return False

print(is_url("https://example.com"))  # True
print(is_url("example.com"))          # False（没有scheme）


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
    url = get_setu_lilicon(False, tag)
    try:
        if is_url(url):
            await setu.finish(Message(f'[CQ:image,file={url}]'))
        else:
            await setu.finish(url)
    except Exception as e:
        logger.error(f"发生错误: {e}, url: {url}")
        await setu.send("发生错误,请检查API是否正常.")
        await setu.finish(url)
        