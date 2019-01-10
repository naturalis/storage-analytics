#!/bin/bash
#
# retrieve size statistics of all aws restic buckets and return in json
# requires jq and git
#
#

ANSIBLE_RESTIC_REPODIR=/opt/ansible-manage-restic-keys
ANSIBLE_RESTIC_REPO=https://github.com/naturalis/ansible-manage-restic-keys
ANSIBLE_RESTIC_REPOFILE=$ANSIBLE_RESTIC_REPODIR/backup_sets
DATE=`date +"%Y-%m-%dT%T%:z"`
HOST=`hostname -f`
DATA_ID=""
DATA_STATUS="production"
DATA_HOST=""
STORAGE_TYPE="backup"
STORAGE_LOCATION="AWS"
STORAGE_POOL=""

# clone repo if no repo found
if [ ! -d "$ANSIBLE_RESTIC_REPODIR" ]; then
  git clone $ANSIBLE_RESTIC_REPO $ANSIBLE_RESTIC_REPODIR 
fi

# pull latest version
(cd /opt/ansible-manage-restic-keys && git pull)

cat $ANSIBLE_RESTIC_REPOFILE | grep "\[restic-clients\]" -A 99999 |  grep -v "\[restic-clients\]" | while read client
do
now=$(date +%s)
data_amount=`aws cloudwatch get-metric-statistics \
                            --namespace AWS/S3 \
                            --start-time "$(echo "$now - 86400" | bc)" \
                            --end-time "$now" \
                            --period 86400 \
                            --statistics Average \
                            --region eu-central-1 \
                            --metric-name NumberOfObjects \
                            --dimensions Name=BucketName,Value="restic-$client" Name=StorageType,Value=AllStorageTypes \
                            | jq '.Datapoints | .[] | .Average'`
data_size=`aws cloudwatch get-metric-statistics \
                            --namespace AWS/S3 \
                            --start-time "$(echo "$now - 86400" | bc)" \
                            --end-time "$now" \
                            --period 86400 \
                            --statistics Average \
                            --region eu-central-1 \
                            --metric-name BucketSizeBytes \
                            --dimensions Name=BucketName,Value="restic-$client" Name=StorageType,Value=StandardStorage \
                            | jq '.Datapoints | .[] | .Average'`

jq --arg key0   '@timestamp' \
   --arg value0 "$DATE" \
   --arg key1   'host' \
   --arg value1 "$HOST" \
   --arg key2   'data_set' \
   --argjson value2 "{\"name\":\"Restic backup waarneming-web\",\"id\":\"restic-waarneming-web\"}" \
   --arg key3   'data_id' \
   --arg value3 "$DATA_ID" \
   --arg key4   "data_status" \
   --arg value4 "$DATA_STATUS" \
   --arg key5   "data_size" \
   --arg value5 "$data_size" \
   --arg key6   "data_amount" \
   --arg value6 "$data_amount" \
   --arg key7   "data_owner" \
   --argjson value7 "{\"name\":\"ICT Infra\"}" \
   --arg key8   "data_groups" \
   --argjson value8 "{}" \
   --arg key9   "data_host" \
   --arg value9 "$DATA_HOST" \
   --arg key10   "data_service_tags" \
   --argjson value10 "[\"restic\",\"$client\"]" \
   --arg key11   "storage_id" \
   --arg value11 "restic-$client" \
   --arg key12   "storage_path" \
   --arg value12  "s3:https://s3.amazonaws.com/restic-$client" \
   --arg key13   "storage_type" \
   --arg value13 "$STORAGE_TYPE" \
   --arg key14   "storage_location" \
   --arg value14 "$STORAGE_LOCATION" \
   --arg key15   "storage_pool" \
   --arg value15 "$STORAGE_POOL" \
   '. | .[$key0]=$value0 | .[$key1]=$value1 | .[$key2]=$value2 | .[$key3]=$value3 | .[$key4]=$value4 | .[$key5]=$value5 | .[$key6]=$value6 | .[$key7]=$value7 | .[$key8]=$value8 | .[$key9]=$value9 | .[$key10]=$value10 | .[$key11]=$value11 | .[$key12]=$value12 | .[$key13]=$value13 | .[$key14]=$value14 | .[$key15]=$value15'\
   <<<'{}'

done

