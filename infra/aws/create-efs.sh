EFS_VOLUMES=(metabase_postgres_db fuseki_data ted_sws logs dags airflow_postgres_db mongo_db)
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
  echo "Volume $1 successfully created "
}


echo "Creating volumes ..."
for EFS_VOLUME in "${EFS_VOLUMES[@]}"
do
  create_volume $EFS_VOLUME
done