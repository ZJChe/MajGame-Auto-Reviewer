from playwright.sync_api import sync_playwright, TimeoutError
import time
import base64
from nonebot import logger

def get_table_pic(cid, round, school):
    """
    获取指定学校的比赛结果截图
    :param cid: 比赛ID
    :param round: 轮次
    :param school: 学校名称
    :return: base64 编码的图片字符串，或 None（失败）
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            url = f"https://cdn.r-mj.com/?cid={cid}#!ranking_Log_{round}"
            page.goto(url, wait_until="networkidle")

            # 查找包含学校名的表格
            target_table = page.locator(f"table:has-text('{school}')").first

            if not target_table or target_table.count() == 0:
                print(f"未找到包含学校 “{school}” 的表格。")
                return None

            image_bytes = target_table.screenshot(type="png")
            base64_str = "base64://" + base64.b64encode(image_bytes).decode("utf-8")
            return base64_str

    except TimeoutError as e:
        print(f"[超时错误] 页面加载或元素等待超时: {e}")
        logger.error(f"[大凤林截图模块 超时错误] 页面加载或元素等待超时: {e}, url: {url}")
        return None
    except Exception as e:
        print(f"[未知错误] 获取截图失败: {e}")
        logger.error(f"[大凤林截图模块 未知错误] 获取截图失败: {e}, url: {url}")
        return None

if __name__ == "__main__":
    begin = time.time()
    print(get_table_pic("200", "8", "上海交通大学"))
    end = time.time()
    print("耗时：", end - begin)
