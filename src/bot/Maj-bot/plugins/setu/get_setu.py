import requests

def get_setu_lilicon(r18: bool = False, tag: str = None) -> str:
    """
    获取色图from lilicon
    :return: 色图链接
    """
    url = "https://api.lolicon.app/setu/v2"
    params = {
        "r18": 1 if r18 else 0,
        "size": "original",
        "num": 1
    }
    if tag is not None:
        params["tag"] = tag
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["urls"]["original"]
    except requests.RequestException as e:
        return f"请求失败: {e}"
    except ValueError:
        return "解析响应失败，请检查API是否正常。"
    except KeyError:
        return "响应格式错误，请检查API是否正常。"
    except Exception as e:
        return f"发生错误: {e}"

if __name__ == "__main__":
    url = get_setu_lilicon(r18=True, tag="白丝")
    print(url)
