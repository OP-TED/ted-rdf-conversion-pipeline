#!/bin/bash
source .env
export $(cat .env | xargs)
SERVICES_WITH_DNS_CREATION=(sftp digest-api fuseki)
SERVICES_WITHOUT_DNS=(airflow metabase mongo-express worker)
CLUSTER_NAME=ted-sws

start_service_with_service_discovery(){
  ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region $REGION --ecs-profile $CLUSTER_NAME-profile --cluster-config $CLUSTER_NAME-cluster --private-dns-namespace ted_sws --vpc $VPC_ID --dns-type A --enable-service-discovery --create-log-groups --launch-type FARGATE
}

start_service_without_service_discovery(){
  if [ "$1" = "worker" ]; then
    ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region $REGION --ecs-profile $CLUSTER_NAME-profile --cluster-config $CLUSTER_NAME-cluster --create-log-groups --launch-type FARGATE
    ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml service scale 4 --ecs-profile $CLUSTER_NAME-profile --cluster-config $CLUSTER_NAME-cluster --cluster $CLUSTER_NAME-cluster
  else
      ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region $REGION --ecs-profile $CLUSTER_NAME-profile --cluster-config $CLUSTER_NAME-cluster --create-log-groups --launch-type FARGATE
  fi
}


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
