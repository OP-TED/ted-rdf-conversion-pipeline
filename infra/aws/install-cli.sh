#!/bin/bash
#curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
#unzip awscliv2.zip
#sudo ./aws/install
AWS_SECRETS_MANAGER_NAME=ted_sws_2
SERVICES=(mongo digest-api airflow fuseki metabase mongo-express)

EFS_VOLUMES=(metabase_postgres_db fuseki_data ted_sws logs dags airflow_postgres_db mongo_db)
echo "Creating env file ..."
aws secretsmanager create-secret --secret-string file://s.json --name $AWS_SECRETS_MANAGER_NAME
aws secretsmanager get-secret-value --secret-id $AWS_SECRETS_MANAGER_NAME | jq -r '.SecretString' | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' > .env
source .env
export $(cat .env | xargs)


create_volume(){
  echo "Creating volume $1"
  aws efs create-file-system --performance-mode generalPurpose --encrypted --tags Key=Name,Value=$1 > $1-file-system.json
  FILE_SYSTEM_ID=`jq -r ".FileSystemId" $1-file-system.json`
  FILE_SYSTEM_ARN=`jq -r ".FileSystemArn" $1-file-system.json`
  EFS_VOLUME_NAME=$1
  echo ${EFS_VOLUME_NAME^^}_VOLUME_ID=$FILE_SYSTEM_ID >> .env
  rm $1-file-system.json
  echo "Volume system id = $FILE_SYSTEM_ID"
  sleep 5
  aws efs create-mount-target --file-system-id $FILE_SYSTEM_ID --subnet-id $SUBNET_1_ID
  aws efs create-mount-target --file-system-id $FILE_SYSTEM_ID --subnet-id $SUBNET_2_ID
  aws efs create-mount-target --file-system-id $FILE_SYSTEM_ID --subnet-id $SUBNET_3_ID
}


echo "Creating volumes ..."
for EFS_VOLUME in "${EFS_VOLUMES[@]}"
do
  create_volume $EFS_VOLUME
done

source .env
export $(cat .env | xargs)

create_cluster_config_and_profiles() {
  ecs-cli configure --cluster $1-cluster --default-launch-type EC2 --config-name $1-cluster --region eu-west-3
  ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name $1-cluster-profile
}

for SERVICE in "${SERVICES[@]}"
do
  create_cluster_config_and_profiles $SERVICE
done

create_cluster() {
  ecs-cli up --force --keypair amazon --capability-iam --size 1 --instance-type $1 --cluster-config $2 --ecs-profile $3 --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID,$SUBNET_3_ID --security-group $SECURITY_GROUP
}

create_cluster $MONGO_INSTANCE_TYPE mongo-cluster mongo-cluster-profile
create_cluster $DIGEST_API_INSTANCE_TYPE digest-api-cluster digest-api-cluster-profile
create_cluster $AIRFLOW_INSTANCE_TYPE airflow-cluster airflow-cluster-profile
create_cluster $FUSEKI_INSTANCE_TYPE fuseki-cluster fuseki-cluster-profile
create_cluster $METABASE_INSTANCE_TYPE metabase-cluster metabase-cluster-profile
create_cluster $MONGO_EXPRESS_INSTANCE_TYPE mongo-express-cluster mongo-express-cluster-profile



start_service_with_service_discovery(){
  ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region eu-west-3 --ecs-profile $1-cluster-profile --cluster-config $1-cluster --private-dns-namespace ted_sws --vpc $VPC_ID --dns-type A --enable-service-discovery --create-log-groups
}

start_service_without_service_discovery(){
  ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region eu-west-3 --ecs-profile $1-cluster-profile --cluster-config $1-cluster --create-log-groups
}


SERVICES_WITH_DNS_CREATION=(mongo digest-api fuseki)
SERVICES_WITHOUT_DNS=(airflow metabase mongo-express)

for SERVICE in "${SERVICES_WITH_DNS_CREATION[@]}"
do
  echo "Starting $SERVICE service"
  start_service_with_service_discovery $SERVICE
done

for SERVICE in "${SERVICES_WITHOUT_DNS[@]}"
do
  echo "Starting $SERVICE service"
  start_service_without_service_discovery $SERVICE
done


