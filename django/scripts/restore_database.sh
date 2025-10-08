#!/bin/bash
# Usage :
# ./restore_database postgresql://user:password@host.name:port/database
# Durée d'exécution : entre 10 et 40 minutes.

# Lancement du script en mode strict (non officiel).
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

mkdir -p ${BACKUPS_FOLDER_PATH}
database_restoration_url=$1

if [[ ! -n ${database_restoration_url} ]]; then
  echo "Il manque l'URL de la base de données. Fin du script."
  exit 0
fi

if [[ ! -n ${RCLONE_S3_ACCESS_KEY_ID} ]]; then
  echo "Ce script a besoin que Rclone soit correctement configuré."
  echo "Vérifiez que vous avez toutes les variables d'environnement requises."
  echo "Fin du script."
  exit 0
fi

if type rclone 2>/dev/null; then
  echo "Rclone est déjà installé."
else
  rclone_version='1.71.2'
  wget https://downloads.rclone.org/v${rclone_version}/rclone-v${rclone_version}-linux-amd64.zip
  # https://github.com/rclone/rclone/releases/download/v1.71.2/MD5SUMS
  if [[ $(echo "6238ac7cb4c9eb83f1b1f5077c931c22  rclone-v${rclone_version}-linux-amd64.zip" | md5sum --check) != "rclone-v${rclone_version}-linux-amd64.zip: OK" ]]; then
      echo '🙈 Le hash de rclone est différent de celui qui est attendu. Fin du script.'
      exit 0
  fi
  unzip rclone-v${rclone_version}-linux-amd64.zip
  mv "rclone-v${rclone_version}-linux-amd64/rclone" rclone
  chmod +x rclone
  export PATH="${PWD}:${PATH}"
fi

rclone_last_backup="$(rclone lsf --files-only --max-age 48h docurba:/docurba-backups | sort --reverse --key 1 | head -n 1)"
rclone copy --max-age 48h "docurba:/docurba-backups/${rclone_last_backup}" "${BACKUPS_FOLDER_PATH}"

# Le fichier compressé est supprimé lors de la décompression.
gzip --decompress "${BACKUPS_FOLDER_PATH}/${rclone_last_backup}"

files_count=$(ls -1 ${BACKUPS_FOLDER_PATH} | wc -l)
if [[ ${files_count} -gt 1 ]]; then
  echo "Plus d'un fichier de sauvegarde décompressé mais un seul est attendu."
  echo "Arrêt du script."
  exit 0
fi

backup_file="${BACKUPS_FOLDER_PATH}/$(ls ${BACKUPS_FOLDER_PATH} | head -1)"
echo "${backup_file} téléchargé et décompressé correctement."

# Suppression des chaînes de caractère "https://" ou "http://" pour éviter de réaliser
# des requêtes HTTP vers l'environnement de production par erreur.
# En effet, plusieurs déclencheurs (triggers) ont été configurés pour réaliser des appels
# HTTP vers l'URL de production.
# Voir par exemple  https://github.com/MTES-MCT/Docurba/blob/main/nuxt/daily_dump/steps/sql/status_handler/4-trigger_event_procedure_status_handler.sql#L19
# On ne peut pas simplement supprimer le type de connexion car la fonction `http_get` le remplace
# s'il est manquant. Mais la fonction `net.http_get`, utilisée dans les déclencheurs, ne le remplace pas.
# Dans le doute, je supprime également le premier caractère qui suit le type de connexion.
# Cela peut également remplacer des URL présentes dans les données mais
# j'estime que le fonctionnement est déjà satisfaisant pour une première version.
if [[ ${BACKUPS_DELETE_URL_IN_DUMP_FILE} == "True" ]]; then
  echo "Suppression des URL dans le fichier de sauvegarde."
  sed --expression 's/\(https:\/\/.\|http:\/\/.\)//g' --in-place ${backup_file} # Prend environ 10s.
  echo "URL supprimées."
fi

echo "Début de la restauration."
# Comme décrit dans la documentation de Supabase.
# J'ai supprimé l'option `--variable ON_ERROR_STOP=1` pour restaurer malgré des erreurs.
# `session_replication_role` est déjà ajouté lors de la sauvegarde je ne souhaite
# prendre aucun risque avec les déclencheurs.
# https://www.postgresql.org/docs/15/runtime-config-client.html
# Impossible d'utiliser `pg_restore` avec une archive _plain text_.
psql \
  --command 'SET session_replication_role = replica' \
  --file ${backup_file} \
  --dbname ${database_restoration_url}

# https://supabase.com/docs/guides/troubleshooting/refresh-postgrest-schema
psql \
  --command "NOTIFY pgrst, 'reload schema';"\
  --dbname ${database_restoration_url}

if [[ ${BACKUPS_SUPABASE_GRANT_PRIVILEGES_TO_USERS} == "True" ]]; then
  echo "Définition des droits d'accès."
  psql \
    --file "${HOME}/scripts/grant_usage_and_privileges.sql" \
    --dbname ${database_restoration_url}
fi
echo "La restauration est terminée !"

# Ne conservons pas une copie locale trop longtemps.
rm ${backup_file}
echo "Le fichier de sauvegarde est supprimé. Fin du script."
