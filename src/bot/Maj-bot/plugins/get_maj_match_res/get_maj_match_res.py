import base64
from bs4 import BeautifulSoup
import imgkit
from io import BytesIO
import json
import os
from PIL import Image
import requests

url_rank = "https://score.hieuzest.xyz/?cid="

def crop_whitespace(image_path, output_path):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    pixels = img.load()
    bound = 0
    for x in range(width):
        r, g, b = pixels[x, height-50]
        if (r, g, b) != (255, 255, 255):
            bound = x
    for x in range(width):
        r, g, b = pixels[width-x-1, height-50]
        if (r, g, b) != (255, 255, 255):
            img= img.crop((0, 0, width-x+bound, height))
    
    return img

def set_cfg(match: str, team: str, group_id: str):
    if os.path.exists('config.json'):
        with open('config.json', 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    else:
        cfg = {}

    if group_id in cfg:
        group_cfg = cfg[group_id]
    else:
        group_cfg = {
            "match_id": "",
            "team_name": ""
            }
    if match is not None:
        group_cfg["match_id"] = match
    if team is not None:
        group_cfg["team_name"] = team
    
    cfg[group_id] = group_cfg

    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

def get_maj_match_res(group_id: str, match_id : str = None, team_name : str = None)-> str:
    # For debugging purpose only, don't set these two arguments when deploying
    if match_id is None and team_name is None:
        if not os.path.exists('config.json'):
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        with open('config.json', 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        if group_id not in cfg:
            return "该群组没有配置过观赛对象, 请联系管理员设置"
        match_id = cfg[group_id]["match_id"]
        team_name = cfg[group_id]["team_name"]
    
    response = requests.get(url_rank+match_id, timeout=5)
    if response.status_code != 200:
        return f"查询的比赛代码{match_id}可能不存在"
    # 假设 response 是你之前 requests.get() 得到的 Response
    html_page = response.content.decode('utf-8')  # bytes -> str
    soup = BeautifulSoup(html_page, 'html.parser')

    # 1. 拆分成 (纯文本, table_tag) 的列表
    groups = []
    for tag in soup.body.children:
        if tag.name == 'p':
            tbl = tag.find_next_sibling('table', class_='gridtable')
            if tbl:
                # 直接把 p_tag 的完整 HTML（包括 <br/>）带出来
                p_html = str(tag)
                if (team_name in str(tbl)):
                    groups.append((p_html, tbl))
    
    if (len(groups) < 1):
        return f"关注的队伍{team_name}不在比赛中"
    elif (len(groups) > 1):
        return f"查询到多个{team_name}队伍在比赛中, 请检查队伍名称是否设置准确"

    # 3. imgkit 配置
    options = {
        'encoding': 'UTF-8',
        'quiet': '',
        'enable-smart-width': ''
    }

    # 4. 公共的 CSS 样式
    css = """
    /* gridtable */
    table.gridtable {
        font-family: Verdana,
                    Arial,
                    "Microsoft YaHei",        /* Windows 微软雅黑 */
                    "Noto Sans CJK SC",       /* Google Noto 简体 */
                    "WenQuanYi Micro Hei",    /* Linux 常见中文 */
                    sans-serif;
        font-size:12px;
        color:#333333;
        border-width: 1px;
        border-color: #666666;
        border-collapse: collapse;
    }
    table.gridtable th {
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #666666;
        background-color: #dedede;
    }
    table.gridtable td {
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #666666;
    }
    table.gridtable tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    table.gridtable tr:nth-child(odd) {
        background-color: #ffffff;
    }
    table.gridtable tr.highlight {
        background-color: rgba(255, 204, 51, 0.8); 
    }
    table.gridtable tr.lowlight td {
        background-color: rgba(102, 153, 0, 0.8);
    }
    table.gridtable tr.upgrade td {
        background-color: rgba(255, 153, 153, 0.8);
    }
    table.gridtable tr.downgrade td {
        background-color: rgba(153, 255, 153, 0.8);
    }
    /* /gridtable */
    
    """

    # 5. 逐组渲染、输出图片
    for idx, (text, table_tag) in enumerate(groups, start=1):
        html_fragment = f"""<!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <style>{css}</style>
            </head>
            <body>
            <p>{text}</p>
            {str(table_tag)}
            </body>
            </html>"""

        out_path = f'./group_{idx}.png'
        imgkit.from_string(
            html_fragment,
            out_path,
            options=options,
            # config=config
        )
        img = crop_whitespace(out_path, out_path)
        os.remove(out_path)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return  base64.b64encode(buffered.getvalue()).decode('utf-8')

if __name__ == "__main__":
    print(get_maj_match_res("", "200", "上海交通大学"))