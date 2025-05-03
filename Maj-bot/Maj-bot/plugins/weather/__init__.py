from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters import Message

from .get_weather import get_weather

weather = on_command("天气", rule=to_me(), aliases={"weather", "查天气"}, priority=10, block=True)

@weather.handle()
async def handle_function(args: Message = CommandArg()):
    # 提取参数纯文本作为地名，并判断是否有效
    if location := args.extract_plain_text():
        weather_info = get_weather(location)
        await weather.finish(f"{weather_info}")
    else:
        await weather.finish("请输入地名")

