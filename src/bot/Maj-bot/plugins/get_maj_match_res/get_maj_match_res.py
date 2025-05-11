import base64
from bs4 import BeautifulSoup
import imgkit
from io import BytesIO
import json
import os
from PIL import Image, ImageDraw, ImageFont
import requests

url_rank = "https://score.hieuzest.xyz/?cid="
url_detail_meta = "https://cdn.r-mj.com/api/data.php?t=admin&cid="
url_detail_team = "https://cdn.r-mj.com/api/data.php?t=team&cid="
url_detail_round = "https://cdn.r-mj.com/api/data.php?t=class&cid="
url_detail_data = "https://cdn.r-mj.com/api/data.php?t=c_data&cid=CID&r=R"

def crop_whitespace(image_path, output_path) -> Image:
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

def set_cfg(match: str, team: str, group_id: str) -> tuple[str, str]:
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
    return (cfg[group_id]["match_id"], cfg[group_id]["team_name"])


def download_img(url: str, save_path: str):
    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    with open(save_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def get_maj_match_res_detail(match_id : str, team_name : str)->str:
    # Get team ID
    response = requests.get(url_detail_team+match_id, timeout=5)
    if response.status_code != 200:
        raise Exception(f"查询的比赛代码{match_id}可能不存在")
    data_team = response.json()
    if data_team == []:
        raise Exception(f"查询的比赛代码{match_id}可能尚未开赛")
    tid = -1
    for team in data_team:
        if data_team[team]['t_name'] == team_name:
            tid = data_team[team]['tid']
            break
    if tid == -1:
        raise Exception(f"关注的队伍{team_name}不在比赛中")

    # Get meta
    response = requests.get(url_detail_meta+match_id, timeout=5)
    if response.status_code != 200:
        raise Exception(f"查询的比赛代码{match_id}可能不存在")
    meta = response.json()
    match_name = str(meta['t_type']).split('\r\n')
    match_name_set = set()
    for i in range(0, len(match_name)):
        if (match_name[i]) not in match_name_set:
            match_name_set.add(match_name[i])
        else:
            match_name[i-1] = match_name[i-1]+"1"
            match_name[i] = match_name[i]+"2"
    c_round = meta['c_round']

    # Get round ID
    response = requests.get(url_detail_round+match_id, timeout=5)
    if response.status_code != 200:
            raise Exception(f"查询的比赛代码{match_id}可能不存在")
    data_round = response.json()
    if data_round == []:
        raise Exception(f"查询的比赛代码{match_id}可能尚未开赛")

    while c_round >= 0:
        if c_round == 0:
            raise Exception(f"查询的比赛代码{match_id}可能尚未开赛")
        
        round = None
        for r in data_round:
            if r['round'] == c_round and \
                (r['tid1'] == tid or \
                r['tid2'] == tid or \
                r['tid3'] == tid or \
                r['tid4'] == tid):
                round = r
                break
        if round != None:
            break
        c_round -= 1
    
    response = requests.get(url_detail_data.replace('CID', match_id).replace('R', str(c_round)), timeout=5)
    if response.status_code != 200:
        raise Exception(f"查询的比赛代码{match_id}可能不存在")
    data = response.json()
    if data == []:
        raise Exception(f"查询的比赛代码{match_id}最新轮次: {round['clsmark']}可能尚未开始")
    
    if str(round['rid']) not in data:
        raise Exception(f"当前轮次{round['clsmark']}可能尚未开始或者尚未有结果")
    matches = data[str(round['rid'])]

    # Download Team Logo:
    for i in range(1, 5):
        if data_team[str(round[f'tid{i}'])]['img'] != "":
            download_img(data_team[str(round[f'tid{i}'])]['img'], f'./{i}.png')
    
    # Build Table:
    table = [
        [
            {'text': meta['c_name'] + f"第{round['round']}轮 第{round['t_class']}组 {round['clsmark']}", 'bg':(220,233,249),
            'text_color':(0,0,0),'font_size':32, 'colspan':13}
        ],
        [
            {'text': '队伍', 'bg': (245,245,245), 'text_color': (0,12,117), 'font_size':24},
            *[{'text': data_team[str(round[f'tid{i}'])]['t_name'], 'img': f'./{i}.png' if data_team[str(round[f'tid{i}'])]['img'] != "" else '', 'bg': (245,245,245), 'text_color': (0,12,117), 'font_size':24, 'colspan': 3} for i in range(1,5)],
        ],
        [
            {'text': '分数', 'bg': (255,255,255), 'text_color': (0,0,0), 'font_size':24},
            *[{'text': str(matches[-1][f'num{i}']), 'bg': (255,255,255), 'text_color': (0,0,0), 'font_size':24, 'colspan': 3} for i in range(1,5)],
        ],
        [
            {'text': '场次', 'bg': (245,245,245), 'text_color': (0,0,0), 'font_size':24},
            *[
                *[
                    {'text': '选手', 'bg': (245,245,245), 'text_color': (0,0,0), 'font_size':24},
                    {'text': '得失', 'bg': (245,245,245), 'text_color': (0,0,0), 'font_size':24},
                    {'text': '分数', 'bg': (245,245,245), 'text_color': (0,0,0), 'font_size':24},
                ]*4
            ]
        ],
        *[
            [
                {'text': match_name[i], 'bg': (255,255,255) if i%2==1 else (245,245,245), 'text_color': (0,0,0), 'font_size':24},
                *[
                    elem
                    for j in range(1, 5)
                    for elem in [
                        {'text': matches[i][f'name{j}'],
                        'bg': (255,255,255) if i%2==1 else (245,245,245),
                        'text_color': (0,0,0),
                        'font_size': 24},
                        {'text': ('+' if matches[i][f'pint{j}'] > 0 else '')+str(matches[i][f'pint{j}']),
                        'bg': (255,255,255) if i%2==1 else (245,245,245),
                        'text_color': (57, 69, 124) if matches[i][f'pint{j}'] > 0 else (185, 65, 57),
                        'font_size': 24},
                        {'text': str(matches[i][f'num{j}']),
                        'bg': (255,255,255) if i%2==1 else (245,245,245),
                        'text_color': (0,0,0),
                        'font_size': 24},
                    ]
                ]
            ]
            for i in range(0, len(matches))
        ]
    ]

    # 2. 列宽设置（这里只给基础单列宽度）
    base_col_widths = [80] + [180, 100, 100]*4
    row_height = [50]*len(table)
    row_height[1] = 400
    border = 1
    FONT_PATH = "/usr/local/share/fonts/msjh/msjh.ttc"
    FONTBD_PATH = "/usr/local/share/fonts/msjh/msjhbd.ttc"
    # 动态调整列宽
    tmp_img = Image.new('RGB', (10,10))
    draw    = ImageDraw.Draw(tmp_img)
    max_text_w = [0]*13
    for i in range(4, len(table)):
        row = table[i]
        for col_idx, cell in enumerate(row):
            font = ImageFont.truetype(FONT_PATH,
                                    cell.get('font_size', 16))
            bbox = draw.textbbox((0,0), cell['text'], font=font)
            text_w = bbox[2] - bbox[0]
            if text_w > max_text_w[col_idx]:
                max_text_w[col_idx] = text_w
    for i in range(1, 13, 3):
        base_col_widths[i] = max_text_w[i] + 16
    
    # 3. 计算画布大小（取最大的列数 * 基础宽度 * colspan）
    max_cols = max(sum(cell.get('colspan',1) for cell in row) for row in table)
    img_w = sum(base_col_widths[:max_cols]) + (max_cols+1)*border
    img_h = sum(row_height) + (len(table)+1)*border

    img = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(img)

    # 4. 绘制
    PADDING = 4

    y = border
    for row_idx, row in enumerate(table):
        x = border
        col_idx = 0  # 专门用来追踪是第几列
        for cell in row:
            colspan = cell.get('colspan', 1)
            total_w = sum(base_col_widths[col_idx:col_idx+colspan]) + border*(colspan-1)

            # 画背景
            bg = cell.get('bg', (255,255,255))
            draw.rectangle([x, y, x+total_w, y+row_height[row_idx]], fill=bg)

            # —— 新增：先画图片（如果有）
            if 'img' in cell and cell['img'] != '':
                logo = Image.open(cell['img']).convert("RGBA")
                # 限制 logo 尺寸不超过单元格大小减 PADDING
                max_w = total_w - 2*PADDING
                max_h = row_height[row_idx] - 2*PADDING
                # logo.thumbnail((max_w, max_h), resample=Image.Resampling.LANCZOS)
                logo = logo.resize((row_height[row_idx] - 25*PADDING, row_height[row_idx] - 25*PADDING), resample=Image.Resampling.LANCZOS)
                px = x + (total_w - logo.width)//2
                py = y + (row_height[row_idx] - logo.height)//2
                img.paste(logo, (px, py), logo)

            # —— 再画文字
            if 'text' in cell:
                # 根据行号决定是否用粗体
                font_path = FONTBD_PATH if row_idx <= 1 else FONT_PATH
                font = ImageFont.truetype(font_path, cell.get('font_size', 16))
                bbox = draw.textbbox((0,0), cell['text'], font=font)
                tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
                # 文字依然居中绘制，你也可以把 ty 调上去一些，避免跟图片重叠
                tx = x + (total_w - tw)//2
                # 如果有图片，文字固定画在单元格底部（减去 PADDING 和文字高度）
                if 'img' in cell and cell['img']:
                    ty = y + row_height[row_idx] - th - PADDING*4
                else:
                    ty = y + (row_height[row_idx] - th)//2-5

                draw.text((tx, ty), cell['text'], font=font, fill=cell.get('text_color',(0,0,0)))

            # 画边框
            draw.rectangle([x, y, x+total_w, y+row_height[row_idx]],
                        outline="black", width=border)

            # 更新指针
            x += total_w + border
            col_idx += colspan
        y += row_height[row_idx] + border

    # 删除额外图片
    for i in range(1, 5):
        if os.path.exists(f'./{i}.png'):
            os.remove(f'./{i}.png')

    # 5. 保存
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return "[CQ:image,file=base64://" + base64.b64encode(buffered.getvalue()).decode('utf-8') + "]"

def get_maj_match_res(match_id : str = None, team_name : str = None)-> str:    
    response = requests.get(url_rank+match_id, timeout=5)
    if response.status_code != 200:
        raise Exception(f"查询的比赛代码{match_id}可能不存在")
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
        raise Exception(f"关注的队伍{team_name}不在比赛中")
    elif (len(groups) > 1):
        raise Exception(f"查询到多个{team_name}队伍在比赛中, 请检查队伍名称是否设置准确")

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
        return "[CQ:image,file=base64://" + base64.b64encode(buffered.getvalue()).decode('utf-8') + "]"

if __name__ == "__main__":
    print(get_maj_match_res_detail("200", "上海交通大学"))