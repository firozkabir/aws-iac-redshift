#!/usr/bin/env python3

import argparse
import sys
from iac import aws
from etl import sql_helper
from datetime import datetime
import configparser

def command_create_redshift():
    """
        Responsible for creating a redshift cluster. 
        All the parameters are taken from dwh.cfg file
    """
    
    # trying to get the keys from dwh.cfg file
    try: 
        config = configparser.ConfigParser()
        config.read('dwh.cfg')
        aws_key = config['AWS']['KEY']
        aws_secret = config['AWS']['SECRET']
        aws_region = config['AWS']['REGION']

        
        cluster_id = config['DWH']['DWH_CLUSTER_IDENTIFIER']
        role_name = config['DWH']['DWH_IAM_ROLE_NAME']
        db_name = config['DWH']['DWH_DB']
        db_username = config['DWH']['DWH_DB_USER']
        db_password = config['DWH']['DWH_DB_PASSWORD']
        db_port = int(config['DWH']['DWH_PORT'])
        number_of_nodes = int(config['DWH']['DWH_NUM_NODES'])
        cluster_type = config['DWH']['DWH_CLUSTER_TYPE']
        node_type = config['DWH']['DWH_NODE_TYPE']


    except Exception as e:
        print("Encountered following exception while trying to retrieve parameters from dwh.cfg file")
        print(f"{e}")
        sys.exit(1)    
    
    redshift_connection_string = aws.create_redshift_cluster(aws_key=aws_key,
                                                            aws_secret=aws_secret,
                                                            aws_region=aws_region,
                                                            cluster_id=cluster_id,
                                                            role_name=role_name,
                                                            db_name=db_name,
                                                            db_username=db_username,
                                                            db_password=db_password,
                                                            db_port=db_port,
                                                            number_of_nodes=number_of_nodes,
                                                            cluster_type=cluster_type,
                                                            node_type=node_type)
    
    
    
    if redshift_connection_string:
        print(f"Testing redshift connection: {redshift_connection_string}")
        if sql_helper.check_redshift_connection(redshift_connection_string):
            print("Redshift connection successful")
        else:
            print("Redshift connection failed")



def command_delete_redshift():
    """
        Deletes the redshift cluster defined as DWH_CLUSTER_IDENTIFIER in DWH section of dwh.cfg
    """
    # trying to get the keys from dwh.cfg file
    try: 
        config = configparser.ConfigParser()
        config.read('dwh.cfg')
        aws_key = config['AWS']['KEY']
        aws_secret = config['AWS']['SECRET']
        aws_region = config['AWS']['REGION']
        cluster_id = config['DWH']['DWH_CLUSTER_IDENTIFIER']
        role_name = config['DWH']['DWH_IAM_ROLE_NAME']
    except Exception as e:
        print("Encountered following exception while trying to retrieve parameters from dwh.cfg file")
        print(f"{e}")
        sys.exit(1)

    if aws.delete_redshift_cluster(cluster_id=cluster_id,
                                        role_name=role_name,
                                        aws_key=aws_key, 
                                        aws_secret=aws_secret
                                    ):
                    
        print(f"delete_redshift command successful for cluster {cluster_id}")
        print(f"cleaning up roles used  for this cluster")
        
        if aws.cleanup_redshift_role(role_name=role_name,
                                    aws_key=aws_key,
                                    aws_secret=aws_secret,
                                    aws_region=aws_region
                                ):
            print(f"Cleanup of role {role_name} successful")
        else:
            print(f"Cleanup of role {role_name} failed.")
    else:
        print(f"delete_redshift command failed for cluster {cluster_id}")



def command_check_credentials():
    """
        A simple command to check your aws credentials
        Reads the dwh.cfg file, extracts KEY and SECRET values from [AWS] section. 
        Then calls the AWS STS Service to verify the credentials, prints metadata supplied by STS.
    """
    
    # trying to get the keys from dwh.cfg file
    try: 
        config = configparser.ConfigParser()
        config.read('dwh.cfg')
        aws_key = config['AWS']['KEY']
        aws_secret = config['AWS']['SECRET']

    except Exception as e:
        print("Encountered following exception while trying to retrieve KEY and SECRET from dwh.cfg file")
        print(f"{e}")
        sys.exit(1)

    # now calling STS service with the credentials retrieved for verification
    if not aws.check_credentials(aws_key=aws_key, 
                                aws_secret=aws_secret):
        print("credential check failed. exiting program with exit code 1")
        sys.exit(1)


def command_check_redshift_connection():
    """
        A simple command to check redshift connection is working
        Uses the DWH_DB_CONNECTION_STRING parameter in DWH section of dwh.cfg file
    """
    # trying to get the keys from dwh.cfg file
    try: 
        config = configparser.ConfigParser()
        config.read('dwh.cfg')
        db_connection_string = config['DWH']['DWH_DB_CONNECTION_STRING']
    except Exception as e:
        print("Encountered following exception while trying to retrieve DWH_DB_CONNECTION_STRING from dwh.cfg file")
        print(f"{e}")
        sys.exit(1)

    # now calling STS service with the credentials retrieved for verification
    if sql_helper.check_redshift_connection(db_connection_string):
        print(f"Redshift connection to {db_connection_string} successful")
    else:
        print(f"Redshift connection to {db_connection_string} failed")



def main(argv):

    cli_parser = argparse.ArgumentParser(prog='dwh',
                                        usage='%(prog)s --command <check_credentials | create_redshift | delete_redshift | check_redshift>',
                                        description='Cloud data warehouse application for udacity data engineering nano degree'
                                        )
    
    # Add the arguments
    cli_parser.add_argument('--command',
                            metavar='command',
                            action='store',
                            type=str,
                            required=True
                            )
    
    args = cli_parser.parse_args()
    user_command = args.command
    


    print(f"*** start - {datetime.now()} ***")
    
    if user_command == "create_redshift":
        command_create_redshift()
    
    elif user_command == "delete_redshift":
        command_delete_redshift()
    
    elif user_command == "check_credentials":
        command_check_credentials()
    
    elif user_command == "check_redshift":
        command_check_redshift_connection()

    else:
        print(f"User command {user_command} is not recognized.")
        cli_parser.print_help()
        sys.exit(0)

    print(f"=== end - {datetime.now()} ===")


if __name__ == "__main__":
    main(sys.argv)