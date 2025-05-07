from typing import Annotated

from nonebot import on_command, on_message, on_shell_command
from nonebot.rule import to_me, startswith, shell_command, ArgumentParser, Namespace
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.adapters.onebot.v11 import Event, Bot, Message

from .get_maj_match_res import get_maj_match_res, set_cfg

parser = ArgumentParser()
parser.add_argument("-m", "--match", default=None)
parser.add_argument("-t", "--team", default=None)

mres = on_shell_command("mres", priority=10, block= True, parser=parser)

admins = ['1548999469', '3263919697']

@mres.handle()
async def handle_mres(foo: Annotated[Namespace, ShellCommandArgs()], event: Event):
    arg_dict = vars(foo)
    match = arg_dict.get("match")
    team = arg_dict.get("team")

    group_id = event.get_session_id().split("_")[1].strip()
    if match or team:
        if event.get_user_id() not in admins:
            await mres.finish("你没有权限修改观赛配置, 请联系管理员")
        else:
            set_cfg(match=match, team=team, group_id=group_id) 
            await mres.finish(f"已在群组[{group_id}]中设置关注比赛id[{match}]队伍[{team}]") 
    else:
        res = get_maj_match_res(group_id=group_id)
        await mres.finish(Message(f'[CQ:image,file={res}]'))