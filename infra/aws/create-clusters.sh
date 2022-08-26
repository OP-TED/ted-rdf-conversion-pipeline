source .env
export $(cat .env | xargs)
CLUSTERS=(mongo digest-api airflow fuseki metabase mongo-express)

create_cluster_config_and_profiles() {
  ecs-cli configure --cluster $1-cluster --default-launch-type EC2 --config-name $1-cluster --region $REGION
  ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name $1-cluster-profile
}

for CLUSTER in "${CLUSTERS[@]}"
do
  create_cluster_config_and_profiles $CLUSTER
done

create_cluster() {
  echo "VPC ID is $VPC_ID"
  echo "Creating cluster for $1"
  ecs-cli up --force --instance-role ecsInstanceRole --extra-user-data botocore.sh --keypair tedSWS --size 1 --instance-type $1 --cluster-config $2 --ecs-profile $3 --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID --security-group $SECURITY_GROUP
}

create_cluster $MONGO_INSTANCE_TYPE mongo-cluster mongo-cluster-profile
create_cluster $DIGEST_API_INSTANCE_TYPE digest-api-cluster digest-api-cluster-profile
create_cluster $AIRFLOW_INSTANCE_TYPE airflow-cluster airflow-cluster-profile
create_cluster $FUSEKI_INSTANCE_TYPE fuseki-cluster fuseki-cluster-profile
create_cluster $METABASE_INSTANCE_TYPE metabase-cluster metabase-cluster-profile
create_cluster $MONGO_EXPRESS_INSTANCE_TYPE mongo-express-cluster mongo-express-cluster-profile
