#!/usr/bin/env python3

import argparse
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

    cli_parser = argparse.ArgumentParser(prog='dwh',
                                         usage='%(prog)s --command <check_credentials | create_redshift | delete_redshift>',
                                         description='Cloud data warehouse application for udacity data engineering nano degree')
    
    # Add the arguments
    cli_parser.add_argument('--command',
                            metavar='command',
                            action='store',
                            type=str,
                            required=True
                            )
    
    args = cli_parser.parse_args()
    user_command = args.command
    print(user_command)
    
    print(f"*** start - {datetime.now()} ***")

    # get command from argv
    
    if user_command == "create_redshift":
        aws.create_redshift_cluster()
    
    elif user_command == "delete_redshift":
        aws.delete_redshift_cluster()
    
    elif user_command == "check_credentials":
        if not aws.check_aws_credentials():
            print("credential check failed. exiting program with exit code 1")
            sys.exit(1)
    else:
        print(f"User command {user_command} is not recognized.")
        cli_parser.print_help()
        sys.exit(0)

    print(f"=== end - {datetime.now()} ===")


if __name__ == "__main__":
    main(sys.argv)