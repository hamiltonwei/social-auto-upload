# Provides a CLI for the automatic social uploading process.
# usage: social_uploader --upload --platforms xhs tencent douyin tiktok
import argparse
import json
from uploaders.master_uploader import MasterUploader


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


if __name__ == "__main__":
    # TODO: Video title isn't being filled in the title bar for douyin.
    valid_platforms = {"douyin", "tencent"}

    args = parse_cli()
    config = parse_config()
    uploader = MasterUploader(config)
    if args.upload and check_platform_validity():
        for platform in args.platforms:
            uploader.upload(platform)