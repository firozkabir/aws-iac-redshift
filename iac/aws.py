import boto3

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