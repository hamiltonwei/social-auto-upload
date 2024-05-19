"""Including abstractions of a single Video upload session for different platforms"""
# -*- coding: utf-8 -*-
import json
from datetime import datetime
from playwright.async_api import Playwright, async_playwright
import asyncio

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from utils.files_times import get_absolute_path


# TODO: add an abstract base class "Video" so all these other classes can inherit.

class DouYinVideo(object):
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
        # 选择包含特定文本内容的 label 元素
        label_element = page.locator("label.radio--4Gpx6:has-text('定时发布')")
        # 在选中的 label 元素下点击 checkbox
        await label_element.click()
        await asyncio.sleep(1)
        publish_date_hour = publish_date.strftime("%Y-%m-%d %H:%M")

        await asyncio.sleep(1)
        await page.locator('.semi-input[placeholder="日期和时间"]').click()
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.type(str(publish_date_hour))
        await page.keyboard.press("Enter")

        await asyncio.sleep(1)

    async def handle_upload_error(self, page):
        print("视频出错了，重新上传中")
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        # 使用 Chromium 浏览器启动一个浏览器实例
        if self.local_executable_path:
            browser = await playwright.chromium.launch(headless=False, executable_path=self.local_executable_path)
        else:
            browser = await playwright.chromium.launch(headless=False)
        # 创建一个浏览器上下文，使用指定的 cookie 文件
        context = await browser.new_context(storage_state=f"{self.account_file}")

        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://creator.douyin.com/creator-micro/content/upload")
        print('[+]正在上传-------{}.mp4'.format(self.title))
        # 等待页面跳转到指定的 URL，没进入，则自动等待到超时
        print('[-] 正在打开主页...')
        await page.wait_for_url("https://creator.douyin.com/creator-micro/content/upload")
        # 点击 "上传视频" 按钮
        await page.locator(".upload-btn--9eZLd").set_input_files(self.file_path)

        # 等待页面跳转到指定的 URL
        while True:
            # 判断是是否进入视频发布页面，没进入，则自动等待到超时
            try:
                await page.wait_for_url(
                    "https://creator.douyin.com/creator-micro/content/publish?enter_from=publish_page")
                break
            except:
                print("  [-] 正在等待进入视频发布页面...")
                await asyncio.sleep(0.1)


        await asyncio.sleep(1)
        print("  [-] 正在填充标题和话题...")

        # 填充标题和话题
        # 检查是否存在包含输入框的元素
        # 这里为了避免页面变化，故使用相对位置定位：作品标题父级右侧第一个元素的input子元素
        # title_container = page.get_by_text('作品标题').locator("..").locator("xpath=following-sibling::div[1]").locator("input")
        # titlecount = title_container.count()
        # if await titlecount:
        #     await title_container.fill(self.title[:30])
        # else:

        # fill in the short title
        await page.get_by_placeholder("作品标题").fill(self.short_title[:30])
        # fill in the content
        titlecontainer = page.locator(".notranslate")
        await titlecontainer.click()
        print("clear existing title")
        await page.keyboard.press("Backspace")
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.press("Delete")
        print("filling new  title")
        await page.keyboard.type(self.title)
        await page.keyboard.press("Enter")
        css_selector = ".zone-container"
        for index, tag in enumerate(self.tags, start=1):
            print("正在添加第%s个话题" % index)
            await page.type(css_selector, "#" + tag)
            await page.press(css_selector, "Space")

        while True:
            # 判断重新上传按钮是否存在，如果不存在，代表视频正在上传，则等待
            try:
                #  新版：定位重新上传
                number = await page.locator('div label+div:has-text("重新上传")').count()
                if number > 0:
                    print("  [-]视频上传完毕")
                    break
                else:
                    print("  [-] 正在上传视频中...")
                    await asyncio.sleep(2)

                    if await page.locator('div.progress-div > div:has-text("上传失败")').count():
                        print("  [-] 发现上传出错了...")
                        await self.handle_upload_error(page)
            except:
                print("  [-] 正在上传视频中...")
                await asyncio.sleep(2)

        # self._enter_location(page)

        # 頭條/西瓜
        third_part_element = '[class^="info"] > [class^="first-part"] div div.semi-switch'
        # 定位是否有第三方平台
        if await page.locator(third_part_element).count():
            # 检测是否是已选中状态
            if 'semi-switch-checked' not in await page.eval_on_selector(third_part_element, 'div => div.className'):
                await page.locator(third_part_element).locator('input.semi-switch-native-control').click()

        if self.publish_date != 0:
            await self.set_schedule_time(page, self.publish_date)

        # 判断视频是否发布成功
        while True:
            # 判断视频是否发布成功
            try:
                publish_button = page.get_by_role('button', name="发布", exact=True)
                if await publish_button.count():
                    await publish_button.click()
                await page.wait_for_url("https://creator.douyin.com/creator-micro/content/manage",
                                        timeout=1500)  # 如果自动跳转到作品页面，则代表发布成功
                print("  [-]视频发布成功")
                break
            except:
                print("  [-] 视频正在发布中...")
                await page.screenshot(full_page=True)
                await asyncio.sleep(0.5)

        await context.storage_state(path=self.account_file)  # 保存cookie
        print('  [-]cookie更新完毕！')
        await asyncio.sleep(2)  # 这里延迟是为了方便眼睛直观的观看
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

    async def _enter_location(self, page):
        await page.locator('div.semi-select span:has-text("输入地理位置")').click()
        await asyncio.sleep(1)
        print("clear existing location")
        # await page.keyboard.press("Backspace")
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.press("Delete")
        await page.keyboard.type("杭州市")
        await asyncio.sleep(1)
        await page.locator('div[role="listbox"] [role="option"]').first.click()


class TencentVideo(object):
    def __init__(self, title, file_path, tags, publish_date: datetime, account_file, category=None, short_title=""):
        self.title = title  # 视频标题
        self.short_title = short_title
        self.file_path = file_path
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = account_file
        self.category = category
        self.local_executable_path = ""  # change me necessary！

    async def set_schedule_time(self, page, publish_date):
        print("click schedule")

        label_element = page.locator("label").filter(has_text="定时").nth(1)
        await label_element.click()

        await page.click('input[placeholder="请选择发表时间"]')

        str_month = str(publish_date.month) if publish_date.month > 9 else "0" + str(publish_date.month)
        current_month = str_month + "月"
        # 获取当前的月份
        page_month = await page.inner_text('span.weui-desktop-picker__panel__label:has-text("月")')

        # 检查当前月份是否与目标月份相同
        if page_month != current_month:
            await page.click('button.weui-desktop-btn__icon__right')

        # 获取页面元素
        elements = await page.query_selector_all('table.weui-desktop-picker__table a')

        # 遍历元素并点击匹配的元素
        for element in elements:
            if 'weui-desktop-picker__disabled' in await element.evaluate('el => el.className'):
                continue
            text = await element.inner_text()
            if text.strip() == str(publish_date.day):
                await element.click()
                break

        # 输入小时部分（假设选择11小时）
        await page.click('input[placeholder="请选择时间"]')
        await page.keyboard.press("Control+KeyA")
        await page.keyboard.type(str(publish_date.hour) + ":" + str(publish_date.minute))

        # 选择标题栏（令定时时间生效）
        await page.locator("div.input-editor").click()

    async def handle_upload_error(self, page):
        print("视频出错了，重新上传中")
        await page.locator('div.media-status-content div.tag-inner:has-text("删除")').click()
        await page.get_by_role('button', name="删除", exact=True).click()
        file_input = page.locator('input[type="file"]')
        await file_input.set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        # 使用 Chromium (这里使用系统内浏览器，用chromium 会造成h264错误
        if self.local_executable_path:
            browser = await playwright.firefox.launch(headless=False, executable_path=self.local_executable_path)
        else:
            browser = await playwright.firefox.launch(headless=False)
        # 创建一个浏览器上下文，使用指定的 cookie 文件
        context = await browser.new_context(storage_state=f"{self.account_file}")

        # 创建一个新的页面
        page = await context.new_page()
        # 访问指定的 URL
        await page.goto("https://channels.weixin.qq.com/platform/post/create")
        print('[+]正在上传-------{}.mp4'.format(self.title))
        # 等待页面跳转到指定的 URL，没进入，则自动等待到超时
        await page.wait_for_url("https://channels.weixin.qq.com/platform/post/create")
        # await page.wait_for_selector('input[type="file"]', timeout=10000)
        file_input = page.locator('input[type="file"]')
        await file_input.set_input_files(self.file_path)
        # 填充标题和话题
        await self._add_title_tags(page)
        # 添加商品
        # await self.add_product(page)
        # 合集功能
        await self._add_collection(page)
        # 原创选择
        await self._add_original(page)
        # 检测上传状态
        await self._detact_upload_status(page)
        if self.publish_date != 0:
            await self.set_schedule_time(page, self.publish_date)
        # 添加短标题
        await self._add_short_title(page)

        await self._click_publish(page)

        await context.storage_state(path=f"{self.account_file}")  # 保存cookie
        print('  [-]cookie更新完毕！')
        await asyncio.sleep(2)  # 这里延迟是为了方便眼睛直观的观看
        # 关闭浏览器上下文和浏览器实例
        await context.close()
        await browser.close()
        print('[+]正在监控执行计划中.......')

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

    async def _add_short_title(self, page):
        short_title_element = page.get_by_text("短标题", exact=True).locator("..").locator(
            "xpath=following-sibling::div").locator(
            'span input[type="text"]')
        if await short_title_element.count():
            short_title = self._format_str_for_short_title()
            await short_title_element.fill(short_title)

    async def _click_publish(self, page):
        while True:
            try:
                publish_buttion = page.locator('div.form-btns button:has-text("发表")')
                if await publish_buttion.count():
                    await publish_buttion.click()
                await page.wait_for_url("https://channels.weixin.qq.com/platform/post/list", timeout=1500)
                print("  [-]视频发布成功")
                break
            except Exception as e:
                current_url = page.url
                if "https://channels.weixin.qq.com/platform/post/list" in current_url:
                    print("  [-]视频发布成功")
                    break
                else:
                    print(f"  [-] Exception: {e}")
                    print("  [-] 视频正在发布中...")
                    await page.screenshot(full_page=True)
                    await asyncio.sleep(0.5)

    async def _detact_upload_status(self, page):
        while True:
            # 匹配删除按钮，代表视频上传完毕，如果不存在，代表视频正在上传，则等待
            try:
                # 匹配删除按钮，代表视频上传完毕
                if "weui-desktop-btn_disabled" not in await page.get_by_role("button", name="发表").get_attribute(
                        'class'):
                    print("  [-]视频上传完毕")
                    break
                else:
                    print("  [-] 正在上传视频中...")
                    await asyncio.sleep(2)
                    # 出错了视频出错
                    if await page.locator('div.status-msg.error').count() and await page.locator(
                            'div.media-status-content div.tag-inner:has-text("删除")').count():
                        print("  [-] 发现上传出错了...")
                        await self.handle_upload_error(page)
            except:
                print("  [-] 正在上传视频中...")
                await asyncio.sleep(2)

    async def _add_title_tags(self, page):
        await page.locator("div.input-editor").click()
        await page.keyboard.type(self.title)
        await page.keyboard.press("Enter")
        for index, tag in enumerate(self.tags, start=1):
            await page.keyboard.type("#" + tag)
            await page.keyboard.press("Space")
        print(f"成功添加hashtag: {len(self.tags)}")

    async def _add_collection(self, page):
        collection_elements = page.get_by_text("添加到合集").locator("xpath=following-sibling::div").locator(
            '.option-list-wrap > div')
        if await collection_elements.count() > 1:
            await page.get_by_text("添加到合集").locator("xpath=following-sibling::div").click()
            await collection_elements.first.click()

    async def _add_original(self, page):
        if await page.get_by_label("视频为原创").count():
            await page.get_by_label("视频为原创").check()
        # 检查 "我已阅读并同意 《视频号原创声明使用条款》" 元素是否存在
        label_locator = await page.locator('label:has-text("我已阅读并同意 《视频号原创声明使用条款》")').is_visible()
        if label_locator:
            await page.get_by_label("我已阅读并同意 《视频号原创声明使用条款》").check()
            await page.get_by_role("button", name="声明原创").click()
        # 2023年11月20日 wechat更新: 可能新账号或者改版账号，出现新的选择页面
        if await page.locator('div.label span:has-text("声明原创")').count() and self.category:
            # 因处罚无法勾选原创，故先判断是否可用
            if not await page.locator('div.declare-original-checkbox input.ant-checkbox-input').is_disabled():
                await page.locator('div.declare-original-checkbox input.ant-checkbox-input').click()
                if not await page.locator(
                        'div.declare-original-dialog label.ant-checkbox-wrapper.ant-checkbox-wrapper-checked:visible').count():
                    await page.locator('div.declare-original-dialog input.ant-checkbox-input:visible').click()
            if await page.locator('div.original-type-form > div.form-label:has-text("原创类型"):visible').count():
                await page.locator('div.form-content:visible').click()  # 下拉菜单
                await page.locator(
                    f'div.form-content:visible ul.weui-desktop-dropdown__list li.weui-desktop-dropdown__list-ele:has-text("{self.category}")').first.click()
                await asyncio.sleep(1)
                if await page.locator('button:has-text("声明原创"):visible').count():
                    await page.locator('button:has-text("声明原创"):visible').click()

    def _format_str_for_short_title(self) -> str:
        # 定义允许的特殊字符
        allowed_special_chars = "《》“”:+?%°"

        # 移除不允许的特殊字符
        filtered_chars = [char if char.isalnum() or char in allowed_special_chars else ' ' if char == ',' else '' for
                          char in self.short_title]
        formatted_string = ''.join(filtered_chars)

        # 调整字符串长度
        if len(formatted_string) > 16:
            # 截断字符串
            formatted_string = formatted_string[:16]
        elif len(formatted_string) < 6:
            # 使用空格来填充字符串
            formatted_string += ' ' * (6 - len(formatted_string))

        return formatted_string


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

    async def create_browser_context(self, playwright):
        if self.local_executable_path:
            browser = await playwright.chromium.launch(headless=False, executable_path=self.local_executable_path)
        else:
            browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=f"{self.account_file}")
        page = await context.new_page()
        return page, context, browser

    async def handle_upload_error(self, page):
        print("视频出错了，重新上传中")
        await page.locator('div.progress-div [class^="upload-btn-input"]').set_input_files(self.file_path)

    async def upload(self, playwright: Playwright) -> None:
        # Create a new browser context and login
        page, context, browser = await self.create_browser_context(playwright)

        # wait for upload page to load
        await page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
        print('[+]正在上传-------{}.mp4'.format(self.title))
        await page.wait_for_url("https://creator.xiaohongshu.com/publish/publish?source=official")

        # upload file
        await page.get_by_role("textbox").set_input_files(self.file_path)

        # fill in short title, title, tags
        await self._add_title_tags(page)
        # set scheduling
        if self.publish_date != 0:
            await self._set_schedule_time(page)

        # Click publish
        await self._click_publish(page)

        # CLean up after finish.
        await context.storage_state(path=f"{self.account_file}")  # 保存cookie
        print('  [-]cookie更新完毕！')
        await asyncio.sleep(2)  # 这里延迟是为了方便眼睛直观的观看
        await context.close()
        await browser.close()
        print('[+]正在监控执行计划中.......')

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)

# =============================== Private Methods =====================================
    async def _set_schedule_time(self, page):
        """
        Set the scheduled publishing time on the uploading page.
        """
        date_placeholder = "请选择日期"
        date_str = self.publish_date.strftime("%Y-%m-%d %H:%M")
        await page.locator("label").filter(has_text="定时发布").locator("div").first.click()
        await page.get_by_placeholder(date_placeholder).click()
        await page.get_by_placeholder(date_placeholder).press("Control+a")
        await page.get_by_placeholder(date_placeholder).fill(date_str)
        await page.get_by_placeholder(date_placeholder).press("Enter")

    async def _add_title_tags(self, page):
        await page.get_by_placeholder("填写标题，可能会有更多赞哦～").fill(self.short_title[:20])
        await page.locator("#post-textarea").fill(self.title + "\n")
        # xhs require you to click on a dropdown menu to "lock in" your hashtag.
        # sometimes your exact hashtag doesn't occur in the dropdown. We just choose the first one.
        for index, tag in enumerate(self.tags):
            await page.keyboard.type("#" + tag)
            try:
                async with asyncio.timeout(2):
                    await page.locator("#tributeContainer").get_by_text(f"#{tag}", exact=True).click()
            except TimeoutError:
                await page.keyboard.press("Enter")

    async def _click_publish(self, page):
        while True:
            try:
                publish_button = page.get_by_role("button", name="发布")
                if await publish_button.count():
                    await publish_button.click()
                await page.wait_for_url(
                    "https://creator.xiaohongshu.com/publish/success?source=official&bind_status=not_bind&__debugger__")
                print("  [-]XHS: Video Published Successfully 视频发布成功")
                break
            except Exception as e:
                current_url = page.url
                if "https://creator.xiaohongshu.com/publish/success" in current_url:
                    print("  [-]视频发布成功")
                    break
                else:
                    print(f"  [-] Exception: {e}")
                    print("  [-] 视频正在发布中...")
                    await page.screenshot(full_page=True)
                    await asyncio.sleep(0.5)

        # https://creator.xiaohongshu.com/publish/success?source=official&bind_status=not_bind&__debugger__
