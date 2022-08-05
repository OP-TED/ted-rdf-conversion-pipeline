REGION=eu-west-3
REPOSITORIES=(fuseki)
MONGO_IMAGE=docker.io/mongo:5.0.10
FUSEKI_IMAGE=docker.io/secoresearch/fuseki:4.5.0
METABASE_IMAGE=docker.io/metabase/metabase:v0.43.4
AIRFLOW_POSTGRES=docker.io/postgres:14.4-alpine

IMAGES_TO_BE_BUILD=(airflow digest-api )

touch .repositories_ids

create_repository(){
  echo "Creating repository for $1"
  aws ecr create-repository --repository-name $1 --image-scanning-configuration scanOnPush=true --region $2 > repo.json
  REPO_NAME=$1
  REPO_ID=`jq -r ".repository.repositoryUri" repo.json`
  echo ${REPO_NAME^^}_REPO_ID=$REPO_ID >> .repositories_ids
  rm repo.json
}



build_image_and_push_to_repo(){
  REPO=$1
  REPO_NAME=${REPO^^}
  REPO_ID=${REPO_NAME}_REPO_ID
  echo ${!REPO_ID}
  aws ecr get-login-password --region eu-west-3 | podman login --username AWS --password-stdin ${!REPO_ID}
  podman build -t $1 ../$1/ --label=$1-image
  IMAGE=`podman images --filter label=$1-image --format {{.Repository}}:{{.Tag}}`
  podman tag $IMAGE ${!REPO_ID}:latest
  podman push ${!REPO_ID}:latest
}



for REPO in "${REPOSITORIES[@]}"
do
#  create_repository $REPO $REGION
  source .repositories_ids
  export $(cat .repositories_ids | xargs)
  build_image_and_push_to_repo $REPO
done


#podman images --filter label=label --format {{.Repository}}
#podman images --format {{.Repository}} | grep fuseki
#
#
#podman build -t fuseki ../fuseki/ --label=label
#
#docker push 013659641721.dkr.ecr.eu-west-3.amazonaws.com/fuseki:latest


#aws ecr get-login-password --region eu-west-3 | podman login --username AWS --password-stdin 013659641721.dkr.ecr.eu-west-3.amazonaws.com
