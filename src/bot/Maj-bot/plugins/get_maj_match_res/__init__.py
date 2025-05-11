import os
import json
from typing import Annotated

from nonebot import on_command, on_message, on_shell_command
from nonebot.rule import to_me, startswith, shell_command, ArgumentParser, Namespace
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.adapters.onebot.v11 import Event, Bot, Message

from .get_maj_match_res import get_maj_match_res, get_maj_match_res_detail, set_cfg

parser = ArgumentParser(add_help=False)
parser.add_argument("-m", "--match", default=None)
parser.add_argument("-t", "--team", default=None)
parser.add_argument("-h", "--help", action='store_true', default=False)

mres = on_shell_command("mres", priority=10, block= True, parser=parser)

admins = ['1548999469', '3263919697']

@mres.handle()
async def handle_mres(foo: Annotated[Namespace, ShellCommandArgs()], event: Event):
    arg_dict = vars(foo)
    match = arg_dict.get("match")
    team = arg_dict.get("team")
    help = arg_dict.get("help")

    group_id = event.get_session_id().split("_")[1].strip()
    if match or team:
        if event.get_user_id() not in admins:
            await mres.finish("你没有权限修改观赛配置, 请联系管理员")
        else:
            match, team = set_cfg(match=match, team=team, group_id=group_id) 
            await mres.finish(f"已在群组[{group_id}]中设置关注比赛id[{match}]队伍[{team}]") 
    elif help:
        await mres.finish("Usage: /mres [OPTIONS]\n\n" \
        "Description:\n\t查询某场比赛的最新详细结果并按队伍筛选。\n\n" \
        "Options:\n"\
        "\t-m, --match <MATCH_ID>   指定比赛编号(整数)，例如 200\n"\
        "\t-t, --team  <TEAM_NAME>  指定队伍名称(字符串)，例如 “上海交通大学”\n"\
        "\t-h, --help  显示本帮助信息") 
    else:
        try:
            if not os.path.exists('config.json'):
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=4)
            with open('config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            if group_id not in cfg:
                raise Exception("该群组没有配置过观赛对象, 请联系管理员设置")
            match_id = cfg[group_id]["match_id"]
            team_name = cfg[group_id]["team_name"]

            try:
                res1 = get_maj_match_res_detail(match_id=match_id, team_name=team_name)
            except Exception as e:
                res1 = str(e)
            try:
                res2 = get_maj_match_res(match_id=match_id, team_name=team_name)
            except Exception as e:
                res2 = str(e)
        except Exception as e:
            await mres.finish(f"{e}")
        await mres.finish(Message(f'{res1}\n{res2}'))