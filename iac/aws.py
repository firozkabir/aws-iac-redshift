import boto3
import botocore
import secrets
import string
import time
from datetime import datetime
import sys

def sleep_countdown(sleep_seconds):
	for i in range(sleep_seconds,0,-1):
		#print(f"{datetime.now()} - waiting {i} seconds.")
		sys.stdout.write("\r")
		sys.stdout.write(f"{datetime.now()} - waiting {i} seconds.")
		sys.stdout.flush()
		time.sleep(1)


def generate_password(length):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))  # for a 20-character password
    return password


def check_aws_credentials() -> bool:

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

def get_role_arn(role_name):

    iam_client = boto3.client('iam')

    try:
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


def create_redshift_cluster(number_of_nodes=2):
    """
     
     source: https://docs.aws.amazon.com/code-samples/latest/catalog/python-redshift-create_cluster.py.html
    """

    print("creating redshift_client")
    
    iam_role_arn = get_role_arn('myRedshiftRole')
    vpc_security_groups = [get_vpc_security_groupid(['redshift_security_group'])]
    iam_roles = [iam_role_arn]
    cluster_identifier = 'redshift-cluster'
    master_username = 'awsuser'
    master_password = generate_password(12)
    db_name = 'dev'

    redshift_client = boto3.client('redshift')
    
    try:
        
        print(f"---> creating redshift cluster {cluster_identifier} with {number_of_nodes} nodes <---")
        print(f"---> database name {db_name}, master_username {master_username} and master_password {master_password} <---")
        print(f"iam_roles {iam_roles}")
        response = redshift_client.create_cluster(
            DBName=db_name,
            Port=5439,
            ClusterIdentifier=cluster_identifier,
            NodeType='dc2.large',
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            VpcSecurityGroupIds=vpc_security_groups,
            #ClusterSubnetGroupName='myredshiftsubnetgroup',
            NumberOfNodes=number_of_nodes,
            IamRoles=iam_roles,)
        
        
        #cluster_status = response.get('Clusters')[0].get('ClusterStatus')
        print(f"create_cluster() called.")
        
        while True:
            
            response = redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)
            cluster_status = response.get('Clusters')[0].get('ClusterStatus')
            
            if cluster_status == 'available':
                break
            
            print(f"{datetime.now()} - cluster status is {cluster_status}. Waiting for cluster to become available")
            print(f"waiting 60 seconds before checking again ....")
            sleep_countdown(60)


    except Exception as e:
        print(f'ERROR: {e}')

def delete_redshift_cluster():
    
    redshift_client = boto3.client('redshift')

    try:
        
        response = redshift_client.delete_cluster(ClusterIdentifier='redshift-cluster',
                                                SkipFinalClusterSnapshot=True
                                                )

        #cluster_status = response.get('Clusters')[0].get('ClusterStatus')
        print(f"delete_cluster() called.")
        
        while True:
            print("Waiting until cluster is deleted, checking every 60 seconds")
            try:
                
                response = redshift_client.describe_clusters(ClusterIdentifier='redshift-cluster')
                cluster_status = response.get('Clusters')[0].get('ClusterStatus')
                
                print(f"{datetime.now()} - cluster status is {cluster_status}. Waiting for cluster to be deleted")
                print("Waiting 60 seconds before checking again")
                sleep_countdown(60)
            
            except botocore.exceptions.ClientError as e:
                print(f"Looks like cluster redshift-cluster has been deleted. {e}")
                break

    except botocore.exceptions.ClientError as e:
        print(f'Looks like cluster redshift-cluster has been deleted. {e}')

