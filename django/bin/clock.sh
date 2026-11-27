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
  # UTC
  current_time=$(date +%H:%M)
  if [[ "$current_time" == "00:05" ]]; then
    django-admin process_denormalized_procedure_fields --yesterday-only
  fi
  if [[ "$current_time" == "00:10" ]]; then
    django-admin process_denormalized_commune_procedure_fields --yesterday-only
  fi
  if [[ "$current_time" == "00:23" ]]; then
    django-admin link_events_with_event_types
  fi
  if [[ "$current_time" == "00:43" ]]; then
    echo "☕ Il est ${current_time} ! C'est l'heure de la sauvegarde !"
    /usr/bin/bash scripts/backup_database.sh "${DATABASE_URL}"
  fi
  if [[ "$current_time" == "03:03" ]]; then
    date_pivot=$(date -I)
    echo "Synchronize procedure status and opposability using events until $date_pivot"
    django-admin update_event_date_by_impact --wet-run
    django-admin synchronize_procedure_status --date_pivot="$date_pivot" --wet-run
    django-admin synchronize_commune_procedure_opposability --date_pivot="$date_pivot" --wet-run
  fi
  sleep 1m
done
