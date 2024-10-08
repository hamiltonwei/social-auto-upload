from datetime import timedelta

from datetime import datetime
from pathlib import Path
import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from conf import BASE_DIR


def get_absolute_path(relative_path: str, base_dir: str = None) -> str:
    # Convert the relative path to an absolute path
    absolute_path = Path(BASE_DIR) / base_dir / relative_path
    return str(absolute_path)


def get_title_and_hashtags(filename):
    """
  获取视频标题和 hashtag

  Args:
    filename: 视频文件名

  Returns:
    视频标题和 hashtag 列表
  """

    # 获取视频标题和 hashtag txt 文件名
    txt_filename = filename.replace(".mp4", ".txt")

    # 读取 txt 文件
    with open(txt_filename, "r", encoding="utf-8") as f:
        content = f.read()

    # 获取标题和 hashtag
    splite_str = content.strip().split("\n")
    # assume short title is empty if there are only two lines in the video meta file.
    if len(splite_str) < 3:
        short_title = ""
        title = splite_str[0]
        hashtags = splite_str[1].replace("#", "").split(" ")
    else:
        short_title = splite_str[0]
        title = splite_str[1]
        hashtags = splite_str[2].replace("#", "").split(" ")

    return title, hashtags, short_title


def generate_schedule_immediate():
    return []


# Should be able customize: when the first upload is, the intervals between uploads
def generate_schedule_interval(total_videos, interval=60, timestamps=False, start_time=130):
    """
    Generate a schedule for video uploads by separating each upload by a fixed time interval

    Args:
    - total_videos: Total number of videos to be uploaded.
    - interval: The number of minutes between each upload.
    - timestamps: Boolean to decide whether to return timestamps or datetime objects.
    - start_time: Start from after start_days.

    Returns:
    - A list of scheduling times for the videos, either as timestamps or datetime objects.
    """
    # Most platforms won't let you schedule a video within two hours from now
    # make it 10 minutes beyond the minimum time to take into account the processing time of other videos
    if start_time < 130:
        start_time = 130
        print("WARNING: Most platforms won't let you schedule a video within 120 min from now. \n"
              "Your start time has been changed to 130 minutes to avoid errors.")

    schedule = []
    current_time = datetime.now()

    for vid_num in range(total_videos):
        time_offset = timedelta(minutes=interval * vid_num + start_time)
        schedule.append(current_time + time_offset)

    if timestamps:
        schedule = [int(time.timestamp()) for time in schedule]
    return schedule


# TODO: Make a separate scheduler class that takes in these parameters as variables.
def generate_schedule_time_next_day(total_videos, videos_per_day, daily_times=None, timestamps=False, start_days=0):
    """
    Generate a schedule for video uploads, starting from the next day.

    Args:
    - total_videos: Total number of videos to be uploaded.
    - videos_per_day: Number of videos to be uploaded each day.
    - daily_times: Optional list of specific times of the day to publish the videos.
    - timestamps: Boolean to decide whether to return timestamps or datetime objects.
    - start_days: Start from after start_days.

    Returns:
    - A list of scheduling times for the videos, either as timestamps or datetime objects.
    """
    if videos_per_day <= 0:
        raise ValueError("videos_per_day should be a positive integer")

    if daily_times is None:
        # Default times to publish videos if not provided
        daily_times = [6, 11, 14, 16, 22]

    if videos_per_day > len(daily_times):
        raise ValueError("videos_per_day should not exceed the length of daily_times")

    # Generate timestamps
    schedule = []
    current_time = datetime.now()

    for video in range(total_videos):
        day = video // videos_per_day + start_days + 1  # +1 to start from the next day
        daily_video_index = video % videos_per_day

        # Calculate the time for the current video
        hour = daily_times[daily_video_index]
        time_offset = timedelta(days=day, hours=hour - current_time.hour, minutes=-current_time.minute,
                                seconds=-current_time.second, microseconds=-current_time.microsecond)
        timestamp = current_time + time_offset

        schedule.append(timestamp)

    if timestamps:
        schedule = [int(time.timestamp()) for time in schedule]
    return schedule


def generate_schedule_time_fixed(iso_datestr):
    return [datetime.fromisoformat(iso_datestr)]


if __name__ == "__main__":
    # quick unit tests
    # print(generate_schedule_interval(10, 120))
    # print(generate_schedule_interval(5, 100, start_time=120))

    title, tag, short_title = get_title_and_hashtags("C:\- Personal Files\Codes\social-auto-upload\\videos\\2023-12-19-instagram.txt")
    print(f"short title:{short_title}\n tile:{title} \ntags:{tag}")
