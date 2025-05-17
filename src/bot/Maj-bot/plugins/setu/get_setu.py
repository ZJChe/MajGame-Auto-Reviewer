import requests
import uuid
import os
import aiohttp
import asyncio

async def download_image_to_unique_file(url: str) -> str:
    """
    下载图片并保存为唯一文件名，返回保存路径
    """
    unique_id = uuid.uuid4().hex
    ext = os.path.splitext(url)[1]
    save_path = f"/tmp/setu_{unique_id}{ext if ext else '.jpg'}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"下载失败，状态码: {resp.status}")
                with open(save_path, "wb") as f:
                    f.write(await resp.read())
        return save_path
    except Exception as e:
        print(f"下载失败: {e}")
        return ""

async def get_setu_lilicon(r18: bool = False, tag: str = None) -> str:
    """
    获取色图并保存为唯一文件，返回本地图片路径或错误信息
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
        img_url = data["data"][0]["urls"]["original"]

        if img_url.startswith("http"):
            return await download_image_to_unique_file(img_url)
        else:
            return "API返回了无效链接"
    except requests.RequestException as e:
        return f"请求失败: {e}"
    except (ValueError, KeyError):
        return "响应格式错误,请检查API是否正常."
    except Exception as e:
        return f"发生错误: {e}"

if __name__ == "__main__":
    local_path = asyncio.run(get_setu_lilicon(r18=True, tag="白丝"))
    print("本地文件路径:", local_path)
