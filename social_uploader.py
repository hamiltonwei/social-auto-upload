
# usage: social_uploader upload --platforms xhs tencent douyin tiktok
import argparse

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


def upload_to_tencent():
    pass
    #TODO: implement tencent upload


def upload_to_douyin():
    pass
    #TODO: implement douyin_upload


def upload():
    """
    Handle uploading to various platforms. Will be called if the "--upload" option is present.
    """
    if not args.platforms:
        print("Please specify at least one valid platforms. \n Currently available platforms are: tencent, douyin")
    else:
        selected_platforms_set = set(args.platforms)
        selected_valid_platforms_set = valid_platforms.intersection(selected_platforms_set)

        # if there are invalid platforms specified (or if a duplicate is found):
        if len(selected_valid_platforms_set) < len(args.platforms):
            print("some of the platforms you specified are not valid. "
                  "\n Currently available platforms are: tencent, douyin")

        # start handling different platforms:
        if "tencent" in selected_platforms_set:
            upload_to_tencent()
            print("Uploading to Tencent...")
        if "douyin" in selected_platforms_set:
            upload_to_douyin()
            print("Uploading to Douyin...")


if __name__ == "__main__":
    valid_platforms = {"douyin", "tencent"}

    args = parse_cli()
    if args.upload:
        upload()


