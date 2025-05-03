import requests
import json

LEVEL_MAX_POINTS = [20, 80, 200, 
                    600, 800, 1000, 
                    1200, 1400, 2000, 
                    2800, 3200, 3600, 
                    4000, 6000, 9000]
PLAYER_RANKS = "初士杰豪圣魂"
MAJSOUL_RANKS = {
    "10301": ("雀杰一", 1200),
    "10302": ("雀杰二", 1400),
    "10303": ("雀杰三", 2000),
    "10401": ("雀豪一", 2800),
    "10402": ("雀豪二", 3200),
    "10403": ("雀豪三", 3600),
    "10501": ("雀圣一", 4000),
    "10502": ("雀圣二", 6000),
    "10503": ("雀圣三", 9000),
}

def get_level_text(username: str, level: dict) -> str:
    if level["id"] < 10700:
        # 不是魂天
        rk = MAJSOUL_RANKS[str(level["id"])]
        return f"{username}: {rk[0]}[{level["score"]+level["delta"]}/{rk[1]}]"
    else:
        # 是魂天
        level_id = level["id"] - 10700
        if level_id < len(LEVEL_MAX_POINTS):
            return f"{username}: 魂天{level_id}[{(level["score"]+level["delta"])/100:.1f}/{20.0}]"



def get_majsoul_pt(username: str, max_users = 3) -> str:
    """
    获取雀魂玩家的PT值
    :param username: 雀魂用户名
    :return: PT值
    """
    get_id = f"https://5-data.amae-koromo.com/api/v2/pl4/search_player/{username}?limit={max_users}&tag=all"
    get_info = "https://5-data.amae-koromo.com/api/v2/pl4/player_stats/{}/1262304000000/1746278399999?mode=16&tag=485077"
    try:
        response = requests.get(get_id, timeout=5)
        infos = json.loads(response.text)
        satisfactory_user = 0

        result_text = ""

        for person in infos:
            nickname = person["nickname"]
            if nickname != username:
                continue
            else:
                satisfactory_user += 1
            result_text += get_level_text(nickname, person["level"])
            if satisfactory_user > 1:
                result_text += "\n"

        return result_text

    except requests.exceptions.Timeout:
        return "请求超时，请稍后再试"
    except requests.RequestException as e:
        return f"获取PT值失败: {e}"
    except Exception as e:
        return f"发生错误: {e}"

if __name__ == "__main__":
    username = "ygmsdr"  
    pt_value = get_majsoul_pt(username)
    print(pt_value)
