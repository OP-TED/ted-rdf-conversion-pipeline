REGION=eu-west-1
MONGO_IMAGE=docker.io/mongo:5.0.10
FUSEKI_IMAGE=docker.io/secoresearch/fuseki:4.5.0
METABASE_IMAGE=docker.io/metabase/metabase:v0.43.4
AIRFLOW_POSTGRES_IMAGE=docker.io/postgres:14.4-alpine
REDIS_IMAGE=docker.io/redis:7.0.4-alpine3.16



IMAGES_TO_BE_BUILD=(airflow digest_api metabase_postgres)
IMAGES_FROM_DOCKER_HUB=(fuseki airflow_postgres metabase mongo redis)

touch .repositories_ids

create_repository(){
  echo "Creating repository for $1"
  aws ecr create-repository --repository-name $1 --region $2 > repo.json
  REPO_NAME=$1
  REPO_ID=`jq -r ".repository.repositoryUri" repo.json`
  echo ${REPO_NAME^^}_REPO_ID=$REPO_ID >> .repositories_ids
  rm repo.json
}



build_image_and_push_to_repo(){
  echo "Building image for $1"
  REPO=$1
  REPO_NAME=${REPO^^}
  REPO_ID=${REPO_NAME}_REPO_ID
  echo ${!REPO_ID}
  aws ecr get-login-password --region $REGION | podman login --username AWS --password-stdin ${!REPO_ID}
  if [ "$REPO" = "metabase_postgres" ]; then
  REPO=metabase
  fi
  podman build -t $REPO ../$REPO/ --label=$1-image
  IMAGE=`podman images --filter label=$1-image --format {{.Repository}}:{{.Tag}}`
  echo "image found is $IMAGE"
  TAG=$(echo $IMAGE| cut -d':' -f 2)
  echo "TAG found is $TAG"
  if [ ! -z $TAG ]
  then
    podman tag $IMAGE ${!REPO_ID}:$TAG
    podman push ${!REPO_ID}:$TAG
  fi

  podman tag $IMAGE ${!REPO_ID}:latest
  podman push ${!REPO_ID}:latest

  echo ${REPO_NAME}_IMAGE_URI=${!REPO_ID}:latest >> .env
  echo "Image for $1 has been pushed in AWS"
  podman system prune --all --force && podman rmi --all
}

get_built_image_and_push_to_repo(){
  echo "Getting image for $1"
  REPO=$1
  REPO_NAME=${REPO^^}
  REPO_ID=${REPO_NAME}_REPO_ID
  IMAGE_TO_PULL=${REPO_NAME}_IMAGE
  echo "REPO_ID=${!REPO_ID}"
  echo ${!IMAGE_TO_PULL}
  aws ecr get-login-password --region $REGION | podman login --username AWS --password-stdin ${!REPO_ID}
  podman pull ${!IMAGE_TO_PULL}
  echo "string to compare is $REPO"
  IMAGE_NAME_TO_FIND=$REPO
  if [ "$REPO" = "airflow_postgres" ]; then
    IMAGE_NAME_TO_FIND=postgres
  fi
  echo " Image to find is $IMAGE_NAME_TO_FIND"
  IMAGE=`podman images --format {{.Repository}}:{{.Tag}} | grep $IMAGE_NAME_TO_FIND`
  echo "image found is $IMAGE"
  TAG=$(echo $IMAGE| cut -d':' -f 2)
  podman tag $IMAGE ${!REPO_ID}:latest
  podman tag $IMAGE ${!REPO_ID}:$TAG
  podman push ${!REPO_ID}:latest
  podman push ${!REPO_ID}:$TAG
  echo ${REPO_NAME}_IMAGE_URI=${!REPO_ID}:latest >> .env
  echo "Image for $1 has been pushed in AWS"
  podman system prune --all --force && podman rmi --all
}

for IMAGE in "${IMAGES_FROM_DOCKER_HUB[@]}"
do
  create_repository $IMAGE $REGION
  source .repositories_ids
  export $(cat .repositories_ids | xargs)
  get_built_image_and_push_to_repo $IMAGE
done

for IMAGE in "${IMAGES_TO_BE_BUILD[@]}"
do
  create_repository $IMAGE $REGION
  source .repositories_ids
  export $(cat .repositories_ids | xargs)
  build_image_and_push_to_repo $IMAGE
done
