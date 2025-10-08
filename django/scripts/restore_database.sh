#!/bin/bash
# This script needs Rclone to be properly configured. Make sure you have all the environment variables needed.
# Usage:
# ./restore_database postgresql://user:password@host.name:port/database

# Run this in the unofficial strict mode.
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

# TODO for review apps: make it work only if backups are needed as it's not possible to activate CRON tasks only in some environment.
# See https://doc.scalingo.com/platform/app/task-scheduling/scalingo-scheduler#dealing-with-multiple-environments
# https://doc.scalingo.com/languages/python/django/start#initialize-your-application-locally

database_restoration_url=$1

if [[ ! -n ${database_restoration_url} ]]; then
  echo "Missing database url to restore to. Exiting."
  exit 0
fi

if type ./rclone 2>/dev/null; then
  echo "Rclone already installed."
else
  echo "Installing rclone."
  wget https://downloads.rclone.org/rclone-current-linux-amd64.zip
  unzip rclone-current-linux-amd64.zip
  mv rclone-*-linux-amd64/rclone rclone
fi

if [[ ! -n ${RCLONE_S3_ACCESS_KEY_ID} ]]; then
  echo "This script needs Rclone to be properly configured. Make sure you have all the environment variables needed."
  exit 0
fi

rclone_last_backup="$(rclone lsf --files-only --max-age 24h docurba:/docurba-backups)"
rclone copy --max-age 24h --progress "docurba:/docurba-backups/${rclone_last_backup}" "${BACKUP_FOLDER_PATH}"

zipped_backup_file="${BACKUP_FOLDER_PATH}/${rclone_last_backup}"
backup_file="${BACKUP_FOLDER_PATH}/$(tar --directory ${BACKUP_FOLDER_PATH} --extract --verbose --file ${zipped_backup_file})"
rm ${zipped_backup_file}

echo "${backup_file} ready to be restored!"
# # Remplace "https://" or "http://" strings by nothing to avoid maing HTTP calls to the production environment.
# We can't just remove the connection type as the `http_get` function replaces it. BUT the net.http_get function does not.
# Don't take any risk and also replace the first URI character.
# This may also any value referencing a URL as the dump also includes data to restore
# but it's good enough for a first version.
if [[ ${DELETE_URL_IN_DUMP_FILE} == "True" ]]; then
  echo "Deleting URL in the dump file."
  sed --expression 's/\(https:\/\/.\|http:\/\/.\)//g' --in-place ${backup_file} # takes about 10s to execute.
  echo "URL deleted in the dump file."
fi

echo "Restoration is starting."
# This is the Supabase way as described in their documentation.
  # --variable ON_ERROR_STOP=1 \
  # https://www.postgresql.org/docs/15/runtime-config-client.html
# session_replication_role is already set in the backup but don't take any risk and set it again.
psql \
  --clean \
  --if-exists \
  --single-transaction \
  --command 'SET session_replication_role = replica' \
  --file ${backup_file} \
  --dbname ${database_restoration_url}

# Make sure we don't keep a copy for too long.
rm "$backup_file"
echo "Restoration is over!"
