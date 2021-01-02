# AWS Infrastructure as Code for Redshift Cluster

A small proejct to create / test / delete Redshift cluster on AWS programatically.
Project is designed to automate the task of spawing and dropping AWS cluster using boto3 python3 sdk. 

## Development Environment Setup 

* Clone this repo:
```bash
git clone git@github.com:firozkabir/aws-iac-redshift.git
```

* Setup python virtual environment and install requirements:
```bash
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip3 install -r requirements.txt 
```

## Configure AWS credentials on your  computer: 

* Using AWL CLI (preferred): 
```bash
aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
# source: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html
```

* Setting environment variables directly in ~/.aws/credentials: 
```bash
echo -e "\nexport aws_access_key_id=AKIAIOSFODNN7EXAMPLE\nexport aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" >> ~/.aws/credentials
# boto3 will check ~/.aws/credentials for credentials by default 
# see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#guide-configuration
```


## Run the program

```bash
./run-aws-iac.sh 
usage: aws-iac-main --command <check_credentials | create_redshift | delete_redshift | check_redshift>
aws-iac-main: error: the following arguments are required: --command
```

### check your credentials against AWS's STS service 
```bash
./run-aws-iac.sh --command check_credentials
```

### create a redshift cluster 
```bash
./run-aws-iac.sh --command create_redshift
```


### check connectivity to your redshift cluster
```bash
./run-aws-iac.sh --command check_redshift
```


### delete the redshift cluster
```bash
./run-aws-iac.sh --command delete_redshift
```



### Credits

Some of the boto3 functions in iac.aws modules were lifted directly from https://docs.aws.amazon.com/code-samples. 
In such cases, the function docstrings mention the url of the code-sample page. 
