#!/bin/bash

cd $(dirname $0)/../../

docker compose up test_db -d
RETRIES=15
until docker compose exec test_db bash -c '(psql -c "select 1 from public.only_exists_in_test;") > /dev/null 2>&1' || [[ ${RETRIES} -eq 0 ]]; do
    echo "Waiting for Postgres server, $((RETRIES--)) remaining attempts..."
    sleep 2
done
cd django
if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
fi
PYTHONPATH=. DJANGO_SETTINGS_MODULE=config.settings.test django-admin migrate
