from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import time
import base64
from nonebot import logger
import requests

url_detail_meta = "https://cdn.r-mj.com/api/data.php?t=admin&cid="

def get_round(cid):
    """
    获取比赛轮次（同步操作）
    """
    response = requests.get(url_detail_meta + cid, timeout=5)
    if response.status_code != 200:
        raise Exception(f"查询的比赛代码 {cid} 可能不存在")
    meta = response.json()
    return meta['c_round']

async def get_table_pic(cid, school):
    """
    获取指定学校的比赛结果截图（异步 Playwright）
    """
    url = None
    try:
        round = get_round(cid)
        url = f"https://cdn.r-mj.com/?cid={cid}#!ranking_Log_{round}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(url, wait_until="networkidle")

            target_table = page.locator(f"table:has-text('{school}')").first
            if await target_table.count() == 0:
                logger.warning(f"未找到包含学校 {school} 的表格")
                return None

            image_bytes = await target_table.screenshot(type="png")
            base64_str = "base64://" + base64.b64encode(image_bytes).decode("utf-8")
            logger.info('成功获取比赛结果截图')
            return f"[CQ:image,file={base64_str}]"

    except PlaywrightTimeoutError as e:
        logger.error(f"[大凤林截图模块 超时错误] 页面加载超时: {e}, url: {url}")
    except Exception as e:
        logger.error(f"[大凤林截图模块 未知错误] 获取截图失败: {e}, url: {url}")
    return None

if __name__ == "__main__":
    import asyncio
    async def main():
        begin = time.time()
        result = await get_table_pic("183", "花莳·上海千寻雀庄")
        print(result)
        print("耗时：", time.time() - begin)

    asyncio.run(main())
