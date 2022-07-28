curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install


SUBNET_1_ID=subnet-0633b255adc732d3f
SUBNET_2_ID=subnet-0088e8035626e7ab5
SUBNET_3_ID=subnet-04ad482119216e427
VPC_ID=vpc-093d2f650f90a4dac
SECURITY_GROUP=sg-03850090ad599ebc6
ACCESS_KEY={$ACCESS_KEY}
SECRET_KEY={$SECRET_KEY}


#aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-093d2f650f90a4dac"
#aws ec2 describe-vpcs --filters Name=tag:Name,Values=Meaningfy


#login


#efs
aws efs create-file-system --performance-mode generalPurpose --tags Key=Name,Value=mongo-db > create-file-system.json
FILE_SYSTEM_ID=`jq -r ".FileSystemId" create-file-system.json`
FILE_SYSTEM_ARN=`jq -r ".FileSystemArn" create-file-system.json`

#find how to get file-system id and subnets ids
aws efs create-mount-target --file-system-id $FILE_SYSTEM_ID --subnet-id $SUBNET_1_ID
aws efs create-mount-target --file-system-id $FILE_SYSTEM_ID --subnet-id $SUBNET_2_ID
aws efs create-mount-target --file-system-id $FILE_SYSTEM_ID --subnet-id $SUBNET_3_ID


#Cluster with ec2 instance and using ecs-cli

ecs-cli configure --cluster mongo-cluster --default-launch-type EC2 --config-name mongo-cluster --region eu-west-3
ecs-cli configure --cluster airflow-cluster --default-launch-type EC2 --config-name airflow-cluster --region eu-west-3
ecs-cli configure --cluster fuseki-cluster --default-launch-type EC2 --config-name fuseki-cluster --region eu-west-3
ecs-cli configure --cluster metabase-cluster --default-launch-type EC2 --config-name metabase-cluster --region eu-west-3
ecs-cli configure --cluster digest-api-cluster --default-launch-type EC2 --config-name digest-api-cluster --region eu-west-3

ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name mongo-cluster-profile
ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name airflow-cluster-profile
ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name fuseki-cluster-profile
ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name metabase-cluster-profile

ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name cli-cluster-profile

ecs-cli up --force --keypair amazon --capability-iam --size 1 --instance-type t2.medium --cluster-config mongo-cluster --ecs-profile mongo-cluster-profile --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID,$SUBNET_3_ID --security-group $SECURITY_GROUP
ecs-cli up --force --keypair amazon --capability-iam --size 1 --instance-type t2.medium --cluster-config fuseki-cluster --ecs-profile fuseki-cluster-profile --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID,$SUBNET_3_ID --security-group $SECURITY_GROUP
ecs-cli up --force --keypair amazon --capability-iam --size 1 --instance-type t3.medium --cluster-config airflow-cluster --ecs-profile airflow-cluster-profile --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID,$SUBNET_3_ID --security-group $SECURITY_GROUP
ecs-cli up --force --keypair amazon --capability-iam --size 1 --instance-type t2.medium --cluster-config metabase-cluster --ecs-profile metabase-cluster-profile --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID,$SUBNET_3_ID --security-group $SECURITY_GROUP

ecs-cli up --force --keypair amazon --capability-iam --size 1 --instance-type t2.micro --cluster-config digest-api-cluster --ecs-profile cli-cluster-profile --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID,$SUBNET_3_ID --security-group $SECURITY_GROUP


ecs-cli compose --project-name mongo-service --file mongo.yml --ecs-params mongo-ecs-params.yml --debug service up --region eu-west-3 --ecs-profile mongo-cluster-profile --cluster-config mongo-cluster --create-log-groups

ecs-cli compose --project-name airflow-service --file airflow.yml --ecs-params airflow-ecs-param.yml --debug service up --region eu-west-3 --ecs-profile airflow-cluster-profile --cluster-config airflow-cluster --create-log-groups

ecs-cli compose --project-name fuseki-service --file fuseki.yml --ecs-params fuseki-ecs-params.yml --debug service up --region eu-west-3 --ecs-profile fuseki-cluster-profile --cluster-config fuseki-cluster --create-log-groups

ecs-cli compose --project-name metabase-service --file fuseki.yml --ecs-params metabase-ecs-params.yml --debug service up --region eu-west-3 --ecs-profile metabase-cluster-profile --cluster-config metabase-cluster --create-log-groups

