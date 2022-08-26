#!/bin/bash
source .env
export $(cat .env | xargs)
SERVICES_WITH_DNS_CREATION=(mongo digest-api fuseki)
SERVICES_WITHOUT_DNS=(airflow metabase)

start_service_with_service_discovery(){
  ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region $REGION --ecs-profile $1-cluster-profile --cluster-config $1-cluster --private-dns-namespace ted_sws --vpc $VPC_ID --dns-type A --enable-service-discovery --create-log-groups
#  ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region $REGION --ecs-profile $1-cluster-profile --cluster-config $1-cluster --private-dns-namespace ted_sws --vpc $VPC_ID --dns-type A --enable-service-discovery
}

start_service_without_service_discovery(){
  ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region $REGION --ecs-profile $1-cluster-profile --cluster-config $1-cluster --create-log-groups
#  ecs-cli compose --project-name $1-service --file $1.yml --ecs-params $1-ecs-params.yml --debug service up --region $REGION --ecs-profile $1-cluster-profile --cluster-config $1-cluster
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
