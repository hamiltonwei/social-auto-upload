# Provides a CLI for the automatic social uploading process.
# usage: social_uploader --upload --platforms xhs tencent douyin tiktok
import argparse
import asyncio
import json

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from uploaders.tencent_uploader.main import weixin_setup, TencentVideo
from uploaders.douyin_uploader.main import douyin_setup, DouYinVideo
from utils.constant import TencentZoneTypes
from utils.files_times import *

def parse_cli():
    """
    Defines the syntax for the command line.
    Returns:
        an args object containing all the arguments passed to the CLI
    """
    parser = argparse.ArgumentParser(description="placeholder arg description")

    parser.add_argument("-u", "--upload",
                         help="upload video to platforms", action="store_true")
    parser.add_argument("-p", "--platforms", nargs='+',
                        help="choose the platforms you want to upload to")

    args = parser.parse_args()
    return args


def check_platform_validity():
    if not args.platforms:
        print("Please specify at least one valid platforms. \n Currently available platforms are: tencent, douyin")
        return False
    else:
        selected_platforms_set = set(args.platforms)
        selected_valid_platforms_set = valid_platforms.intersection(selected_platforms_set)

        # if there are invalid platforms specified (or if a duplicate is found):
        if len(selected_valid_platforms_set) < len(args.platforms):
            print("some of the platforms you specified are not valid and are ignored."
                  "\n Currently available platforms are: tencent, douyin")
        return True


def parse_config():
    with open("config.json", 'r') as file:
        config = json.load(file)
        return config


def prepare_to_upload(config):
    """
    perform some basic preparations routines before starting the upload
    Ret
    """
    vid_dir = config["video_directory"]
    if os.path.isabs(vid_dir):
        filepath = vid_dir
    else:
        filepath = Path(BASE_DIR) / config["video_directory"]

    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    schedule = generate_schedule(file_num, config)

    return files, schedule


def generate_schedule(file_num, config):
    """
    generate an upload schedule for scheduled uploading.
    Parameters:
        - int file_num: Specifies the number of videos to upload.
        - str scheduling_method: A string indicating a scheduling method.
            currently accepted values are "interval", "next_day".
    Returns:
        the upload schedule (list of datetimes objects)
    """
    publish_datetimes = []
    scheduling_method = config["scheduling"]["method"]
    if scheduling_method == "interval":
        interval = config["scheduling"]["interval_settings"]["interval"]
        start_time = config["scheduling"]["interval_settings"]["start_time"]
        publish_datetimes = generate_schedule_interval(file_num, interval, start_time=start_time)
    elif scheduling_method == "next_day":
        vid_per_day = config["scheduling"]["next_day_settings"]["videos_per_day"]
        start_time = config["scheduling"]["next_day_settings"]["start_time"]
        daily_times = config["scheduling"]["next_day_settings"]["daily_times"]
        publish_datetimes = generate_schedule_time_next_day(file_num, vid_per_day, daily_times, start_time=start_time)
    return publish_datetimes


def get_account_file(platform, config):
    """
    generate the account file for the specified platform
    Parameters:
        - str platform:
    Returns:
        the upload schedule (list of datetimes objects)
    """
    acc_dir = config["cookie_directory"]
    if os.path.isabs(acc_dir):
        filepath = acc_dir
    else:
        filepath = Path(BASE_DIR) / config["cookie_directory"]
    account_file = Path(BASE_DIR / filepath / config["cookie_files"][platform])
    return account_file


def print_file_infos(file, title, tags):
    # 打印视频文件名、标题和 hashtag
    print(f"视频文件名：{file}")
    print(f"标题：{title}")
    print(f"Hashtag：{tags}")


def upload_to_tencent(files, account_file, schedule):
    cookie_setup = asyncio.run(weixin_setup(account_file, handle=True))
    category = TencentZoneTypes.LIFESTYLE.value  # 标记原创需要否则不需要传
    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        app = TencentVideo(title, file, tags, schedule[index], account_file, category)
        asyncio.run(app.main(), debug=False)


def upload_to_douyin(files, account_file, schedule):
    cookie_setup = asyncio.run(douyin_setup(account_file, handle=True))
    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        app = DouYinVideo(title, file, tags, schedule[index], account_file)
        asyncio.run(app.main(), debug=False)


def upload(platform, config):
    """
    Handle uploading to various platforms. Will be called if the "--upload" option is present.
    Parameters:
        - str platform: the platform we are uploading to.
    """
    files, schedule = prepare_to_upload(config)
    account_file = get_account_file(platform, config)
    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        print_file_infos(file, title, tags)

    # start handling different platforms:
    if platform == "tencent":
        upload_to_tencent(files, account_file, schedule)
        # print("Uploading to Tencent...")
    elif platform == "douyin":
        upload_to_douyin(files, account_file, schedule)
        # print("Uploading to Douyin...")


if __name__ == "__main__":
    # TODO: Video title isn't being filled in the title bar.
    valid_platforms = {"douyin", "tencent"}

    args = parse_cli()
    config = parse_config()
    if args.upload and check_platform_validity():
        for platform in args.platforms:
            upload(platform, config)


