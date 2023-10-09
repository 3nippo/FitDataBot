set -x

echo "start backup"

export PGPASSWORD=$(cat /run/secrets/db_pwd)

mkdir -p /home/root

pg_dump -f /home/root/dump -h fit_data_db -F c -U postgres fit_data_db

UPLOAD_URL=$(curl -H "Authorization: OAuth $(cat /run/secrets/ya_disk_oauth_token)" 'https://cloud-api.yandex.net/v1/disk/resources/upload?path=app:/dump&overwrite=true' | jq --raw-output .href)

curl -T '/home/root/dump' "$UPLOAD_URL"

echo "end backup"