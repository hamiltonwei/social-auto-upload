from datetime import datetime
from pathlib import Path

from playwright.async_api import Playwright, async_playwright
import os

from conf import BASE_DIR


class PlaywrightAuthenticator():
    """
    A class used to authenticate login for playwright
    """
    def __init__(self):
        """
        Initialize an authenticator.
        Parameters:
            - the platform you want to authenticate
        """
        # Each platform should have
        # - a login_url, used to initialize login process
        # - an auth_url, used to verify the successfulness of the login
        # - a failure_str, where if this string is detected on the page, it would indicate an unsuccessful login.
        self.auth_dict = {
            "douyin":{
                "login_url": "https://www.douyin.com/",
                "auth_url": "https://creator.douyin.com/creator-micro/content/upload",
                "failure_str": "div.boards-more h3:text('抖音排行榜')"},

            "tencent": {
                "login_url": "https://channels.weixin.qq.com",
                "auth_url": "https://channels.weixin.qq.com/platform/post/create",
                "failure_str": 'div.title-name:has-text("视频号小店")'},

            "xhs": {
                "login_url": "https://www.xiaohongshu.com",
                "auth_url": "https://creator.xiaohongshu.com/publish/publish?source=official",
                "failure_str": "短信登录"}
        }

    async def cookie_gen(self, platform, account_file):
        async with async_playwright() as playwright:
            options = {
                'headless': False
            }
            # Make sure to run headed.
            browser = await playwright.chromium.launch(**options)
            # Setup context however you like.
            context = await browser.new_context()  # Pass any options
            # Pause the page, and start recording manually.
            page = await context.new_page()
            await page.goto(self.auth_dict[platform]["auth_url"])
            await page.pause()
            # 点击调试器的继续，保存cookie
            await context.storage_state(path=account_file)

    async def cookie_auth(self, platform, account_file):
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(storage_state=account_file)
            # 创建一个新的页面
            page = await context.new_page()
            # 访问指定的 URL
            await page.goto(self.auth_dict[platform]["auth_url"])
            try:
                await page.wait_for_selector(self.auth_dict[platform]["failure_str"], timeout=5000)  # 等待5秒
                print("[+] 等待5秒 cookie 失效")
                return False
            except:
                print("[+] cookie 有效")
                return True

    async def set_up(self, platform, account_file, handle=False):
        exists = os.path.exists(account_file)
        if not exists or not await self.cookie_auth(platform, account_file):
            if not handle:
                return False
            print('[+] cookie文件不存在或已失效，即将自动打开浏览器，请扫码登录，登陆后会自动生成cookie文件')
            await self.cookie_gen(platform, account_file)
        return True