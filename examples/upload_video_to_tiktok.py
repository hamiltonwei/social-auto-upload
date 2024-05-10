import asyncio
from pathlib import Path


import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from conf import BASE_DIR
from uploaders.tk_uploader.main import tiktok_setup, TiktokVideo
from utils.files_times import generate_schedule_time_next_day, get_title_and_hashtags


if __name__ == '__main__':
    filepath = Path(BASE_DIR) / "videos"
    account_file = Path(BASE_DIR / "tk_uploader" / "account.json")
    folder_path = Path(filepath)
    # get video files from folder
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    publish_datetimes = generate_schedule_time_next_day(file_num, 1, daily_times=[16])
    cookie_setup = asyncio.run(tiktok_setup(account_file, handle=True))
    for index, file in enumerate(files):
        title, tags, short_title = get_title_and_hashtags(str(file))
        print(f"video_file_name：{file}")
        print(f"video_title：{title}")
        print(f"video_hashtag：{tags}")
        app = TiktokVideo(title, file, tags, publish_datetimes[index], account_file)
        asyncio.run(app.main(), debug=False)
