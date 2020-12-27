#!/usr/bin/env python3

import sys
from iac import aws
from datetime import datetime





def get_user_command(argv) -> str:

    user_command = ""

    try:
        user_command = argv[1].strip()
    except Exception as e:
        print(f"Exception getting argv[1]: {e}")
    finally:
        return user_command


def main(argv):

    usage = f"""Usage: {argv[0]} < check_credentials | create_redshift | delete_redshift | help >
                       check_credentials: checks aws credentials found under aws section in aswdwh.cfg file.
                       create_redshift: creates the redshift cluster if does not already exist. 
                       delete_redshift: deletes the redshift cluster if already exists.
                       help: prints this help text.
    """

    print(f"*** start - {argv[0]} - {datetime.now()} ***")

    # get command from argv
    user_command = get_user_command(argv)
    if user_command == "create_redshift":
        pass
    elif user_command == "delete_redshift":
        pass
    elif user_command == "help":
        print(usage)
    elif user_command == "check_credentials":
        if not aws.check_aws_credentials():
            print("credential check failed. exiting program with exit code 1")
            sys.exit(1)

    else:
        print(f"User command {user_command} is not recognized.")
        print(usage)

    print(f"=== end - {argv[0]} - {datetime.now()} ===")


if __name__ == "__main__":
    main(sys.argv)