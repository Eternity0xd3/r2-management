import argparse

def create_parser():
    parser = argparse.ArgumentParser(
        prog="r2",
        description="Personal Cloudflare R2 Management tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    # upload
    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument(
        "files",
        nargs="+"
    )
    group = upload_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--name",
        help="Object name for a single file"
    )
    group.add_argument(
        "--dir",
        help="Object directory for multiple files"
    )

    # list
    subparsers.add_parser("list")

    # download
    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("key")
    download_parser.add_argument("file")

    # delete
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("key")

    return parser

def run(r2, args):
    parser = create_parser()
    parsed = parser.parse_args(args)

    if parsed.command == "upload":
        if parsed.name:
            r2.upload(parsed.files[0], parsed.name)
        elif parsed.dir:
            r2.upload_multiple(parsed.files, parsed.dir)

    elif parsed.command == "list":
        keys = r2.list()
        print(keys)

    elif parsed.command == "download":
        r2.download(parsed.key, parsed.file)

    elif parsed.command == "delete":
        confirmation = input("Are you sure?[y/n]")
        if confirmation.lower() == "y":
            r2.delete(parsed.key)
