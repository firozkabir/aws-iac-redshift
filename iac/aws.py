import boto3
import botocore
import time
from datetime import datetime
import sys
import os
import json

def sleep_countdown(sleep_seconds):
    for i in range(sleep_seconds,0,-1):
        sys.stdout.write("\r")
        sys.stdout.write(f"{datetime.now()} - waiting {i:>2} {'seconds' if i>1 else 'second '}")
        sys.stdout.flush()
        time.sleep(1)
    else:
        sys.stdout.write("\r")
        sys.stdout.write("")
        sys.stdout.flush()


def check_credentials() -> bool:

    try:
        client = boto3.client('sts')

        response = client.get_caller_identity()

        user_id = response.get('UserId')
        account = response.get('Account')
        arn = response.get('Arn')

        print(f"{'-'*15} Checking aws caller identity: {'-'*15}")
        print(f"user_id: {user_id}")
        print(f"account: {account}")
        print(f"arn: {arn}")
        print("-"*61)

        return True

    except Exception as e:
        print(f"Exception when checking credentials: {e}")
        return False



def create_iam_role(role_name: str) -> str:

    """
        Creates a new iam role for redshift cluster and attacheds S3 Readonly Access policy
    """

    role_arn = ''

    try:

        asume_role_policy_json = json.dumps({'Statement': [{'Action': 'sts:AssumeRole',
                                            'Effect': 'Allow',
                                            'Principal': {'Service': 'redshift.amazonaws.com'}}],
                                            'Version': '2012-10-17'}
                                            )

        iam_client = boto3.client('iam')
        
        print("creating the iam role")
        iam_client.create_role(Path='/',
                                RoleName=role_name,
                                Description = "Allows Redshift clusters to call AWS services on your behalf.",
                                AssumeRolePolicyDocument=asume_role_policy_json
                            )    
        
        print("attaching S3ReadOnlyAccess policy")
        iam_client.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")

        response = iam_client.get_role(RoleName=role_name)

        role_arn = response.get('Role').get('Arn')


    except Exception as e:
        print(f"Exception when creating iam role: {e}")
        return role_arn
    
    return role_arn



def get_role_arn(role_name: str) -> str:

    

    try:
        iam_client = boto3.client('iam')
        response = iam_client.get_role(RoleName=role_name)
    except Exception as e:
        print(f'ERROR: {e}')
        return None
    else:
        print(f"Retieved role arn: {response.get('Role').get('Arn')}")
        return response.get('Role').get('Arn')


def get_vpc_security_groupid(group_names):
    ec2_client = boto3.client('ec2')
    try:
        response = ec2_client.describe_security_groups(GroupNames=group_names)
        group_name = response.get('SecurityGroups')[0].get('GroupName')
        group_id = response.get('SecurityGroups')[0].get('GroupId')
        
        print(f"Retrieved security group name: {group_name} and group id: {group_id}")
        
        

    except Exception as e:
        print(f'ERROR: {e}')
        return None
    else:
        
        return group_id


def add_inbound_rule_to_vpc(db_port: int,
                            vpc_id):
    
    try: 
        ec2 = boto3.resource('ec2')
        
        print(f"Trying to open TCP port {db_port} from 0.0.0.0/0 (inbound) for default VPC security group")
        vpc = ec2.Vpc(id=vpc_id)
        default_sg = list(vpc.security_groups.all())[0]
        default_sg.authorize_ingress(GroupName=default_sg.group_name,
                                    CidrIp='0.0.0.0/0',
                                    IpProtocol='TCP',
                                    FromPort=int(db_port),
                                    ToPort=int(db_port)
        )

    except Exception as e:
        print(f"Error while adding inbound rule to vpc: {e}")



def create_redshift_cluster(cluster_id: str,
                            role_name: str,
                            db_name: str,
                            db_username: str,
                            db_password: str,
                            db_port: int,
                            number_of_nodes: int = 2,
                            cluster_type: str = 'multi-node',
                            node_type: str ='dc2.large'
                            ) -> str:
    """
        create a redshift cluster given the parameters suppied
        waits (blocks) and checks every 30 seconds until cluster to become available
        returns the redshift database connection string upon sucdess. 
    """

    return_string = ''

    try:

        print(f"Check if IAM Role {role_name} exists.")
        iam_role_arn = get_role_arn(role_name=role_name)
        
        if not iam_role_arn:
            print("IAM Role {role_name} does not exist. Creating it now.")
            iam_role_arn = create_iam_role(role_name=role_name)
        
        print(f"We will use the role {iam_role_arn}")


        redshift_client = boto3.client('redshift')

        print(f"---> creating redshift cluster {cluster_id} with {number_of_nodes} nodes <---")
        print(f"---> database name {db_name}, db_username {db_username} and db_password {db_password} <---")
        print(f"iam_roles {iam_role_arn}")
        response = redshift_client.create_cluster(
                                                ClusterType=cluster_type,
                                                NodeType=node_type,
                                                NumberOfNodes=number_of_nodes,
                                                DBName=db_name,
                                                ClusterIdentifier=cluster_id,
                                                MasterUsername=db_username,
                                                MasterUserPassword=db_password,
                                                Port=db_port,
                                                IamRoles=[iam_role_arn]
                                                )

        print(f"create_cluster() called.")

        while True:
            
            response = redshift_client.describe_clusters(ClusterIdentifier=cluster_id)
            cluster_status = response.get('Clusters')[0].get('ClusterStatus')
            
            if cluster_status == 'available':
                print(f"\n")
                print(f"{'-'*60}")
                print(f"Cluster created. Here are the details you need:")
                
                cluster_id = response.get('Clusters')[0].get('ClusterIdentifier')
                db_username = response.get('Clusters')[0].get('MasterUsername')
                db_name = response.get('Clusters')[0].get('DBName')
                db_endpoint = response.get('Clusters')[0].get('Endpoint').get('Address')
                db_port = response.get('Clusters')[0].get('Endpoint').get('Port')
                db_connection_string = f"postgresql://{db_username}:{db_password}@{db_endpoint}:{db_port}/{db_name}"
                vpc_id = response.get('Clusters')[0].get('VpcId')

                print(f"cluster_id: {cluster_id}")
                print(f"db_username: {db_username}")
                print(f"db_password: {db_password}")
                print(f"db_name: {db_name}")
                print(f"db_endpoint: {db_endpoint}")
                print(f"db_port: {db_port}")
                print(f"db_connection_string: {db_connection_string}")
                print(f"vpc_id: {vpc_id}")

                print(f"Adding inbound tcp rule to vpc for port {db_port}")
                add_inbound_rule_to_vpc(db_port=db_port, vpc_id=vpc_id)
                
                return_string = db_connection_string

                print(f"{'-'*60}")

                break
            
            print(f"{datetime.now()} - cluster status is **{cluster_status}**; Waiting for cluster to become available")
            wait_seconds = 60
            print(f"waiting {wait_seconds} seconds before checking again ....")
            sleep_countdown(wait_seconds)


    except Exception as e:
        print(f'ERROR: {e}')
    
    finally:
        return return_string


def delete_redshift_cluster(cluster_id: str, role_name: str) -> bool:
    """
        Deletes a given redshift cluster. Skips final snapshot when doing this. 
        Blocks until delete has gone through. 
        Waits and checks every 60 seconds to until delete is complete. 
    """

    outcome = False

    try:
        
        redshift_client = boto3.client('redshift')
        
        response = redshift_client.delete_cluster(ClusterIdentifier=cluster_id,
                                                SkipFinalClusterSnapshot=True
                                                )
        
        print(f"delete_cluster() called.")
        
        while True:

            wait_seconds = 60
            print(f"Waiting until cluster is deleted, checking every {wait_seconds} seconds")

            try:
                
                response = redshift_client.describe_clusters(ClusterIdentifier=cluster_id)
                cluster_status = response.get('Clusters')[0].get('ClusterStatus')
                
                print(f"{datetime.now()} - cluster status is **{cluster_status}**; Waiting for cluster to be deleted")
                
                print(f"Waiting {wait_seconds} seconds before checking again")
                sleep_countdown(wait_seconds)
            
            except botocore.exceptions.ClientError as e:
                print(f"Looks like cluster redshift-cluster has been deleted.")
                outcome = True
                break

    except botocore.exceptions.ClientError as e:
        print(f'Looks like cluster redshift-cluster has been deleted. {e}')

    return outcome


def cleanup_redshift_role(role_name: str) -> bool:
    
    

    try:

        iam_client = boto3.client('iam')
        
        iam_client.detach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess")
        iam_client.delete_role(RoleName=role_name)

    except Exception as e:
        print(f"Exception while cleaning up redshift role: {e}")
        return False
    
    return True


