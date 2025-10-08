#!/bin/bash
# Make a postgres database dumps, then stream the file directly to an S3 bucket.

# Run this in the unofficial strict mode.
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

database_url=$1
backup_file_name=${BACKUP_FOLDER_PATH}/$(date +%Y-%m-%d_%s).sql

if [[ ! -n ${database_url} ]]; then
  echo "Missing database url. Exiting."
  exit 0
fi

if [[ ! -n ${RCLONE_S3_ACCESS_KEY_ID} ]]; then
  echo "This script needs Rclone to be properly configured. Make sure you have all the environment variables needed."
  exit 0
fi

# Dump is created according to an advice from the Supabase's support team.
# https://github.com/mansueli/Supa-Migrate/blob/main/migrate_project.sh
# We export the dump in plain SQL instead of a custom format
# to follow the format of the dump downloadable in the Supabase web interface.
echo "Dumping the database."
  # TODO: remove the auth schema after Supabase's support answer.
pg_dump "${database_url}" \
  --if-exists \
  --clean \
  --quote-all-identifiers \
  --exclude-schema 'extensions|graphql|graphql_public|net|tiger|pgbouncer|vault|realtime|supabase_functions|storage|pg*|information_schema' > ${backup_file_name}

echo "Dumping is done."

# This is also an advice of the support team.
# I guess it's because these schemas are handled by Supabase.
sed --expression 's/^DROP SCHEMA IF EXISTS "auth";$/-- DROP SCHEMA IF EXISTS "auth";/' --in-place ${backup_file_name}
sed --expression 's/^DROP SCHEMA IF EXISTS "storage";$/-- DROP SCHEMA IF EXISTS "storage";/' --in-place ${backup_file_name}
sed --expression 's/^CREATE SCHEMA "auth";$/-- CREATE SCHEMA "auth";/' --in-place ${backup_file_name}
sed --expression 's/^CREATE SCHEMA "storage";$/-- CREATE SCHEMA "storage";/' --in-place ${backup_file_name}
sed --expression 's/^ALTER DEFAULT PRIVILEGES FOR ROLE "supabase_admin"/-- ALTER DEFAULT PRIVILEGES FOR ROLE "supabase_admin"/'\
 --in-place ${backup_file_name}
# This is mandatory to avoid running triggers when restoring.
# https://www.postgresql.org/docs/15/runtime-config-client.html
sed --expression '1s/^/SET session_replication_role = replica;\n/' --in-place ${backup_file_name}

export_file=${BACKUP_FOLDER_PATH}/$(date +%Y-%m-%d_%s).tar.gz
tar cvzf ${export_file} ${backup_file_name}
rm ${backup_file_name}

# Last step: clone to object storage.
# TODO: configure Scalingo to install it.
if type ./rclone 2>/dev/null; then
  echo "Rclone already installed."
else
    wget https://downloads.rclone.org/rclone-current-linux-amd64.zip
    unzip rclone-current-linux-amd64.zip
    mv rclone-*-linux-amd64/rclone rclone
fi

# "rclone copy" copies everything from source to destination
# "rclone move" copies everything from source to destination, then deletes from source
# I removed --progress because it seems to break when run through cron
echo "Sending dump to the S3 bucket."
rclone move --s3-chunk-size=20M ${BACKUP_FOLDER_PATH} docurba:/docurba-backups
echo "Dump sent to S3 bucket."

if [[ ! -n ${BACKUPS_SLACK_WEBHOOK} ]]; then
  echo "Script is over but Slack won't know it as its API key is missing."
  exit 0
fi

# https://docs.slack.dev/app-management/quickstart-app-settings#webhooks
curl -X POST -H 'Content-type: application/json'\
  --data '{"text":"😌 Sauvegarde de la base de données effectuée avec succès."}'\
  ${BACKUPS_SLACK_WEBHOOK}
