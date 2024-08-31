from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright
import asyncio

import os
import sys
import inspect
playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
context = browser.new_context()  # Pass any options
# Pause the page, and start recording manually.
page = context.new_page()
page.goto("https://creator.douyin.com/creator-micro/content/upload")


page.pause()