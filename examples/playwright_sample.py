from playwright.async_api import Playwright, async_playwright
import asyncio


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


async def run(playwright):
    file = "C:\- Personal Files\Codes\social-auto-upload\\videos\\2024-05-05_14-21-38_UTC.mp4"
    cookie = "C:\- Personal Files\Codes\social-auto-upload\cookies\\xhs.json"

    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(storage_state=cookie)

    page = await context.new_page()
    await page.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
    # await page.wait_for_url("https://creator.xiaohongshu.com/publish/publish?source=official")
    # await page.get_by_role("textbox").set_input_files(file)
    await page.pause()

asyncio.run(main())