from datetime import datetime

from playwright.async_api import Playwright, async_playwright
import os
import asyncio


async def xhs_cookie_gen(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.xiaohongshu.com")
        await page.pause()
        # 点击调试器的继续，保存cookie
        await context.storage_state(path=account_file)


async def cookie_auth(account_file):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=account_file)
        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://creator.douyin.com/creator-micro/content/upload")
        try:
            await page.wait_for_selector("短信登录", timeout=5000)  # 等待5秒
            print("[+] 等待5秒 cookie 失效")
            return False
        except:
            print("[+] cookie 有效")
            return True


async def xhs_setup(account_file, handle=False):
    exists = os.path.exists(account_file)
    if not exists or not await cookie_auth(account_file):
        if not handle:
            return False
        print('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
        await xhs_cookie_gen(account_file)
    return True



class XHSVideo(object):
    def __init__(self, title, file_path, tags, publish_date: datetime, account_file, short_title=""):
        self.title = title  # 视频标题
        self.short_title = short_title
        self.file_path = file_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.date_format = '%Y年%m月%d日 %H:%M'
        self.local_executable_path = ""  # change me

    async def set_schedule_time(self, page, publish_date):
        raise NotImplementedError

    async def handle_upload_error(self, page):
        print("视频出错了，重新上传中")
        raise NotImplementedError

    async def _enter_location(self, page):
        raise NotImplementedError

    async def upload(self, playwright: Playwright) -> None:
        raise NotImplementedError

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

