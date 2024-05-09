# Provides a CLI for the automatic social uploading process.
# usage: social_uploader --upload --platforms xhs tencent douyin tiktok
import argparse
import asyncio

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


def prepare_to_upload():
    """
    perform some basic preparations routines before starting the upload
    Ret
    """
    # TODO: these should be read from a config file
    filepath = Path(BASE_DIR) / "videos"
    scheduling_method = "interval"

    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    schedule = generate_schedule(file_num, scheduling_method)

    return files, schedule


def generate_schedule(file_num, scheduling_method="interval"):
    """
    generate an upload schedule for scheduled uploading.
    Parameters:
        - int file_num: Specifies the number of videos to upload.
        - str scheduling_method: A string indicating a scheduling method.
            currently accepted values are "interval", "next_day".
    Returns:
        the upload schedule (list of datetimes objects)
    """
    # TODO: the function parameters should be passed from config file.
    publish_datetimes = []
    if scheduling_method == "next_day":
        publish_datetimes = generate_schedule_time_next_day(file_num, 1, daily_times=[16])
    elif scheduling_method == "interval":
        publish_datetimes = generate_schedule_interval(file_num, interval=1440)
    return publish_datetimes


def get_account_file(platform):
    """
    generate the account file for the specified platform
    Parameters:
        - str platform:
    Returns:
        the upload schedule (list of datetimes objects)
    """
    if platform == "tencent":
        account_file = Path(BASE_DIR / "uploaders" / "tencent_uploader" / "account.json")  # TODO: should be loaded from config
    elif platform == "douyin":
        account_file = Path(BASE_DIR / "uploaders" / "douyin_uploader" / "account.json")
    else:
        return None
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


def upload(platform):
    """
    Handle uploading to various platforms. Will be called if the "--upload" option is present.
    Parameters:
        - str platform: the platform we are uploading to.
    """
    files, schedule = prepare_to_upload()
    account_file = get_account_file(platform)
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


if __name__ == "__main__":
    # TODO: add a config file specifying video directories, upload schedules etc.
    # TODO: Video title isn't being filled in the title bar.
    valid_platforms = {"douyin", "tencent"}

    args = parse_cli()
    if args.upload and check_platform_validity():
        for platform in args.platforms:
            upload(platform)


