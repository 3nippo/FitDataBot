echo "start restore"

export PGPASSWORD=$(cat /run/secrets/db_pwd)

DOWNLOAD_URL=$(curl -H "Authorization: OAuth $(cat /run/secrets/ya_disk_oauth_token)" 'https://cloud-api.yandex.net/v1/disk/resources/download?path=app:/dump' | jq --raw-output .href)

if [[ "$DOWNLOAD_URL" != "null" ]] ; then
    curl -L "$DOWNLOAD_URL" > /tmp/dump

    pg_restore -F c -U postgres -d fit_data_db /tmp/dump

    echo "restored"
    # psql -d $POSTGRES_DB < /tmp/dump
else
    echo "No remote dump"
fi

echo "end restore, rc=$?"