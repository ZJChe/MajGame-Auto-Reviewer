import requests
import uuid
import os
import aiohttp
import asyncio
from PIL import Image

async def download_image_to_unique_file(url: str) -> str:
    """
    下载图片并保存为唯一文件名（含压缩），返回保存路径
    """
    unique_id = uuid.uuid4().hex
    ext = os.path.splitext(url)[1].lower()
    raw_path = f"/tmp/setu_raw_{unique_id}{ext if ext else '.jpg'}"
    compressed_path = f"/tmp/setu_{unique_id}.jpg"

    try:
        # 下载原图
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    raise Exception(f"下载失败，状态码: {resp.status}")
                with open(raw_path, "wb") as f:
                    f.write(await resp.read())

        # 打开并压缩图像（Pillow 10+）
        with Image.open(raw_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            max_width = 2000
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            img.save(compressed_path, quality=85)

        os.remove(raw_path)
        return compressed_path

    except Exception as e:
        print(f"下载或压缩失败: {e}")
        for path in [raw_path, compressed_path]:
            if os.path.exists(path):
                os.remove(path)
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
