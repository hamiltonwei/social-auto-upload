import asyncio


import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from uploaders.video import *
from utils.constant import TencentZoneTypes
from utils.files_times import *
from uploaders.authenticator import PlaywrightAuthenticator

# TODO: make a static method that initialize this class from the config file.

class MasterUploader():
    """
    A "master" uploader class that is capable of uploading to all supported platforms.
    """
    def __init__(self, config):
        # TODO：need to explicitly define the variables instead of just throw it a config file.
        # What if you want to initialize this class for the first time without any config file?
        # What if you want to modify its settings in a gui, without saving it to the config file?
        self.config = config
        self._authenticator = PlaywrightAuthenticator()

    def _prepare_to_upload(self):
        """
        perform some basic preparations routines before starting the upload
        Ret
        """
        vid_dir = self.config["video_directory"]
        if os.path.isabs(vid_dir):
            filepath = vid_dir
        else:
            filepath = Path(BASE_DIR) / vid_dir

        # 获取视频目录
        folder_path = Path(filepath)
        # 获取文件夹中的所有文件
        files = list(folder_path.glob("*.mp4"))
        file_num = len(files)
        schedule = self._generate_schedule(file_num)

        return files, schedule

    def _generate_schedule(self, file_num):
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
        scheduling_method = self.config["scheduling"]["method"]
        if scheduling_method == "interval":
            interval = self.config["scheduling"]["interval_settings"]["interval"]
            start_time = self.config["scheduling"]["interval_settings"]["start_time"]
            publish_datetimes = generate_schedule_interval(file_num, interval, start_time=start_time)
        elif scheduling_method == "next_day":
            vid_per_day = self.config["scheduling"]["next_day_settings"]["videos_per_day"]
            start_days = self.config["scheduling"]["next_day_settings"]["start_days"]
            daily_times = self.config["scheduling"]["next_day_settings"]["daily_times"]
            publish_datetimes = generate_schedule_time_next_day(file_num, vid_per_day, daily_times,
                                                                start_days=start_days)
        elif scheduling_method == "fixed":
            publish_datetimes = generate_schedule_time_fixed(self.config["scheduling"]["fixed_settings"]["iso_datestr"])
        elif scheduling_method == "immediate":
            publish_datetimes = generate_schedule_immediate() #will return empty list.
        return publish_datetimes

    def _get_account_file(self, platform):
        """
        generate the account file for the specified platform
        Parameters:
            - str platform:
        Returns:
            the upload schedule (list of datetimes objects)
        """
        acc_dir = self.config["cookie_directory"]
        if os.path.isabs(acc_dir):
            filepath = acc_dir
        else:
            filepath = Path(BASE_DIR) / self.config["cookie_directory"]
        account_file = Path(BASE_DIR / filepath / self.config["cookie_files"][platform])
        return account_file

    def _print_file_infos(self, file, title, tags, short_title=""):
        # 打印视频文件名、标题和 hashtag
        print(f"视频文件名：{file}")
        print(f"视频短标题：{short_title}")
        print(f"标题：{title}")
        print(f"Hashtag：{tags}")


    def upload(self, platform):
        """
        Handle uploading to various platforms. Will be called if the "--upload" option is present.
        Parameters:
            - str platform: the platform we are uploading to.
        """
        # TODO: BUG - 原创 window doesn't close and have to manually close.
        files, schedule = self._prepare_to_upload()
        account_file = self._get_account_file(platform)
        for index, file in enumerate(files):
            title, tags, short_title = get_title_and_hashtags(str(file))
            self._print_file_infos(file, title, tags, short_title=short_title)

        asyncio.run(self._authenticator.set_up(platform, account_file, handle=True))
        # start handling different platforms:
        # for loop so that we can process all videos as a queue.
        for index, file in enumerate(files):
            title, tags, short_title = get_title_and_hashtags(str(file))

            app = None
            publish_date = None
            if schedule:
                publish_date = schedule[index]

            if platform == "douyin":
                app = DouYinVideo(title, file, tags, publish_date, account_file, short_title=short_title)

            elif platform == "tencent":
                # TODO: should be passed from config/meta data,
                #  but I'm a musician so probably would never change that lol
                # category = TencentZoneTypes.MUSIC.value
                category = TencentZoneTypes.TALENT.value
                app = TencentVideo(title, file, tags, publish_date, account_file, category, short_title=short_title)

            elif platform == "xhs":
                app = XHSVideo(title, file, tags, publish_date, account_file, short_title=short_title)

            asyncio.run(app.main(), debug=False)