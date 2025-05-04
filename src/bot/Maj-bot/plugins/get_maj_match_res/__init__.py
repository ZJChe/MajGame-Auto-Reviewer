from typing import Annotated

from nonebot import on_command, on_message, on_shell_command
from nonebot.rule import to_me, startswith, shell_command, ArgumentParser, Namespace
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.adapters.onebot.v11 import Event, Bot, Message

from .get_maj_match_res import get_maj_match_res

parser = ArgumentParser()
parser.add_argument("-m", "--match", default=None)
parser.add_argument("-t", "--team", default=None)

mres = on_shell_command("mres", priority=10, block= True, parser=parser)

@mres.handle()
async def handle_mres(foo: Annotated[Namespace, ShellCommandArgs()], event: Event):
    arg_dict = vars(foo)
    match = arg_dict.get("match")
    team = arg_dict.get("team")
    await mres.finish(f"{match if match else "0"} {team if team else "1"} {event.get_session_id()}")
    # if match or team:
    #     pass
    # else:
    #     pass
    # await mres.finish(f"123")