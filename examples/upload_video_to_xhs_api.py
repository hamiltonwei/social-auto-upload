import configparser
from pathlib import Path
from time import sleep

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from xhs import XhsClient

from conf import BASE_DIR
from utils.files_times import generate_schedule_time_next_day, get_title_and_hashtags
from uploaders.xhs_api_uploader.main import sign_local, beauty_print

config = configparser.RawConfigParser()
config.read(Path(BASE_DIR / "xhs_uploader" / "accounts.ini"))


if __name__ == '__main__':
    filepath = Path(BASE_DIR) / "videos"
    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)

    cookies = config['account1']['cookies']
    xhs_client = XhsClient(cookies, sign=sign_local, timeout=60)
    # auth cookie
    # 注意：该校验cookie方式可能并没那么准确
    try:
        xhs_client.get_video_first_frame_image_id("3214")
    except:
        print("cookie 失效")
        exit()

    publish_datetimes = generate_schedule_time_next_day(file_num, 1, daily_times=[16])

    for index, file in enumerate(files):
        title, tags, short_title = get_title_and_hashtags(str(file))
        tags_str = ' '.join(['#' + tag for tag in tags])
        # 打印视频文件名、标题和 hashtag
        print(f"视频文件名：{file}")
        print(f"标题：{title}")
        print(f"Hashtag：{tags}")

        topics = []
        # 获取hashtag
        for i in tags[:3]:
            topic_official = xhs_client.get_suggest_topic(i)
            if topic_official:
                topics.append(topic_official[0])

        note = xhs_client.create_video_note(title=title[:20], video_path=str(file), desc=title + tags_str,
                                            topics=topics,
                                            is_private=False,
                                            post_time=publish_datetimes[index].strftime("%Y-%m-%d %H:%M:%S"))

        beauty_print(note)
        # 强制休眠30s，避免风控（必要）
        sleep(30)
