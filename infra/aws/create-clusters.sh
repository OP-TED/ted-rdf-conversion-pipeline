source .env
export $(cat .env | xargs)
CLUSTERS=(ted-sws)

create_cluster_config_and_profiles() {
  ecs-cli configure --cluster $1-cluster --default-launch-type FARGATE --config-name $1-cluster --region $REGION
  ecs-cli configure profile --access-key $ACCESS_KEY --secret-key $SECRET_KEY --profile-name $1-profile
}

for CLUSTER in "${CLUSTERS[@]}"
do
  create_cluster_config_and_profiles $CLUSTER
done

create_cluster() {
  echo "VPC ID is $VPC_ID"
  echo "Creating cluster for $1"
  ecs-cli up --force --cluster-config $2 --ecs-profile $3 --vpc $VPC_ID --subnets $SUBNET_1_ID,$SUBNET_2_ID --security-group $SECURITY_GROUP
}

create_cluster ted-sws ted-sws-cluster ted-sws-profile
