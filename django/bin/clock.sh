#!/bin/bash
#
# Ce script est un ordonnanceur de tâches. Il est exécuté comme
# Custom Clock Process sur Scalingo.
#
# https://doc.scalingo.com/platform/app/task-scheduling/custom-clock-processes
#
# On l'utilise en alternative au Scalingo Scheduler pour exécuter des
# tâches durant plus de 15 minutes.

set -euo pipefail
IFS=$'\n\t'


while true; do
  current_time=$(date +%H:%M)
  # UTC
  if [[ "$current_time" == "00:43" ]]; then
    echo "☕ Il est ${current_time} ! C'est l'heure de la sauvegarde !"
    /usr/bin/bash scripts/backup_database.sh "${DATABASE_URL}"
  fi
  sleep 1m
done
