#!/bin/bash
# Création d'une sauvegarde de la base de données
# puis conservation chiffrée dans un compartiment S3.
# Ce script doit être lancé dans l'environnement de Scalingo car il
# utilise l'utilitaire `dbclient-fetcher` propre à la PaaS.
# Durée d'exécution : entre 20 minutes et 2 heures.

# Lancement du script en mode strict (non officiel).
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

if [[ ! -n ${BACKUPS_ENABLED} ]]; then
  echo "Le système de sauvegarde est inactif."
  exit 0
fi

database_url=$1
mkdir -p ${BACKUPS_FOLDER_PATH}
backup_file_name=${BACKUPS_FOLDER_PATH}/$(date +%Y-%m-%d_%s).sql

if [[ ! -n ${database_url} ]]; then
  echo "Il manque l'URL de la base de données. Fin du script."
  exit 0
fi

if [[ ! -n ${RCLONE_S3_ACCESS_KEY_ID} ]]; then
  echo "Ce script a besoin que Rclone soit correctement configuré."
  echo "Vérifiez que vous avez toutes les variables d'environnement requises."
  echo "Fin du script."
  exit 0
fi

# La version du client PG de Scalingo est la 14 or Supabase est en 15.
# Afin d'assurer une cohérence, il faut effectuer la mise à jour.
# Il n'y a pas d'autre moyen d'indiquer la version de PG.
# https://doc.scalingo.com/platform/databases/access
# Installé dans ${HOME}/bin.
dbclient-fetcher pgsql 15

echo "Réception de la base Supabase."
# La sauvegarde est créée en se basant sur les conseils du support de Supabase.
# https://github.com/mansueli/Supa-Migrate/blob/main/migrate_project.sh
# L'export est réalisé en SQL et non en suivant un format dédié
# (plain sql au lieu de --format c) pour garder le même format que
# celui de la base de données téléchargeable sur l'interface web de Supabase.
${HOME}/bin/pg_dump \
  --verbose \
  --dbname "${database_url}" \
  --if-exists \
  --clean \
  --quote-all-identifiers \
  --no-owner \
  --no-privileges \
  --exclude-schema 'extensions|graphql|graphql_public|net|tiger|pgbouncer|vault|realtime|supabase_functions|storage|pg*|information_schema'\
  --schema '*' > ${backup_file_name}

echo "Réception réalisée."

# Transformation de certaines commandes en commentaires SQL (`--`) sur les conseils
# de l'équipe Support de Supabase.
# Je suppose que c'est dû au fait que ces schémas et ce rôle sont gérés par Supabase directement.
sed --expression 's/^DROP SCHEMA IF EXISTS "auth";$/-- DROP SCHEMA IF EXISTS "auth";/'\
    --expression 's/^DROP SCHEMA IF EXISTS "storage";$/-- DROP SCHEMA IF EXISTS "storage";/'\
    --expression 's/^CREATE SCHEMA "auth";$/-- CREATE SCHEMA "auth";/'\
    --expression 's/^CREATE SCHEMA "storage";$/-- CREATE SCHEMA "storage";/'\
    --expression 's/^ALTER DEFAULT PRIVILEGES FOR ROLE "supabase_admin"/-- ALTER DEFAULT PRIVILEGES FOR ROLE "supabase_admin"/'\
 --in-place ${backup_file_name}
# Nécessaire pour éviter de lancer les déclencheurs (triggers) lors de la restauration.
# https://www.postgresql.org/docs/15/runtime-config-client.html
# L'expression commence par 1 pour indiquer à sed d'exécuter la commande seulement
# sur la première ligne du fichier.
# https://www.gnu.org/software/sed/manual/sed.html#sed-addresses
sed --expression '1s/^/SET session_replication_role = replica;\n/' --in-place ${backup_file_name}

# La compression supprime le fichier d'origine.
gzip --verbose --best ${backup_file_name}

# La condition suivante ne fonctionne pas systématiquement.
# voir https://github.com/MTES-MCT/Docurba/issues/1632
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
  # -u met à jour le paquet dézippé s'il existe déjà.
  unzip -u rclone-v${rclone_version}-linux-amd64.zip
  mv "rclone-v${rclone_version}-linux-amd64/rclone" rclone
  chmod +x rclone
  export PATH="${PWD}:${PATH}"
fi

# `rclone copy` copie tout le contenu de la source vers la destination.
# `rclone move` copie tout le contenu de la source vers la destination puis supprime
# les fichiers du dossier source.
# J'ai supprimé `--progress` car cela semble casser quand la commande est lancée par un cron.
echo "Envoi de la sauvegarde vers le compartiment S3."
rclone move --s3-chunk-size=20M ${BACKUPS_FOLDER_PATH} docurba_backups:/docurba-backups
echo "Sauvegarde envoyée vers le compartiment S3."

if [[ ! -n ${BACKUPS_SLACK_WEBHOOK} ]]; then
  echo "Le script est terminé mais Slack ne le saura pas car il manque la clé d'API."
  exit 0
fi

# https://docs.slack.dev/app-management/quickstart-app-settings#webhooks
curl -X POST -H 'Content-type: application/json'\
  --data '{"text":"😌 Sauvegarde de la base de données effectuée avec succès."}'\
  ${BACKUPS_SLACK_WEBHOOK}

# Sans saut de ligne, ce message est collé au message précédent.
echo -e "\n"
echo "Fin du script."
