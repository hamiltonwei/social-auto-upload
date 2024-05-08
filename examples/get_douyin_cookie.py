import asyncio
from pathlib import Path


import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from conf import BASE_DIR
from douyin_uploader.main import douyin_setup

if __name__ == '__main__':
    account_file = Path(BASE_DIR / "douyin_uploader" / "account.json")
    cookie_setup = asyncio.run(douyin_setup(str(account_file), handle=True))
