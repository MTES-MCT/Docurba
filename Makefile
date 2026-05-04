
# Supabase
start_supabase:
# Use nuxt envrc to start supabase (APP_URL)
# direnv exec DIR COMMAND [...ARGS] : Executes a command after loading the first .envrc or .env found in DIR.
	direnv exec nuxt supabase start

# Django
clean_django:
	rm -Rf django/.venv

install_django:
	cd django && uv venv && . .venv/bin/activate && uv sync

START_DJANGO_CMD := cd django && . .venv/bin/activate && direnv exec . ./manage.py runserver
start_django:
	$(START_DJANGO_CMD)

setup_test_db:
	./docker/test_db/setup_test_db.sh && cd django && direnv exec . django-admin migrate --settings config.settings.test

clean_test_db:
	docker compose down test_db

run_tests_django:
	cd django && pytest . -vv

# Nuxt
clean_nuxt:
	rm -Rf nuxt/{.nuxt,node_modules}

install_nuxt:
	. ${HOME}/.nvm/nvm.sh && cd nuxt && nvm install && nvm use && npm install

START_NUXT_CMD := . ${HOME}/.nvm/nvm.sh && cd nuxt && nvm use && direnv exec . npm run dev
start_nuxt:
	$(START_NUXT_CMD)

# Nuxt3
NUXT3_PATH ?= "../docurba-nuxt3"

clean_nuxt3:
	rm -Rf ${NUXT3_PATH}/{.nuxt,node_modules}

install_nuxt3:
	. ${HOME}/.nvm/nvm.sh && cd ${NUXT3_PATH} && nvm install && nvm use && npm install

START_NUXT3_CMD := . ${HOME}/.nvm/nvm.sh && cd ${NUXT3_PATH} && nvm use && direnv exec . npm run dev
start_nuxt3:
	$(START_NUXT3_CMD)


# All
clean: clean_django clean_nuxt clean_nuxt3

install: install_django install_nuxt install_nuxt3

start: start_supabase
	@trap 'kill $$DJANGO_PID $$NUXT_PID $$NUXT3_PID 2>/dev/null; exit 1' SIGINT SIGTERM; \
	echo "=== Starting Development Environment ==="; \
	\
	echo "Starting django..."; \
	( $(START_DJANGO_CMD) 2>&1 | sed 's/^/[django] /' ) & \
	DJANGO_PID=$$!; \
	echo "django running with PID: $$DJANGO_PID"; \
	\
	echo "Starting nuxt..."; \
	( $(START_NUXT_CMD) 2>&1 | sed 's/^/[nuxt] /' ) & \
	NUXT_PID=$$!; \
	echo "nuxt running with PID: $$NUXT_PID"; \
	\
	echo "Starting nuxt3..."; \
	( $(START_NUXT3_CMD) 2>&1 | sed 's/^/[nuxt3] /' ) & \
	NUXT3_PID=$$!; \
	echo "nuxt3 running with PID: $$NUXT3_PID"; \
	\
	wait $$DJANGO_PID $$NUXT_PID $$NUXT3_PID; \
	echo "=== One process exited. Cleaning up ==="; \
	kill $$DJANGO_PID $$NUXT_PID $$NUXT3_PID 2>/dev/null; \
	exit 0

database_restore: start_supabase
	cd django && direnv exec . ./scripts/restore_database.sh postgresql://postgres:postgres@127.0.0.1:54322/postgres

move_exports_to_outscale:
	cd django && direnv exec . rclone --config scripts/rclone.conf move --s3-chunk-size=20M exports/ docurba_exports:/docurba-exports

copy_exports_from_outscale:
	cd django && direnv exec . rclone --config scripts/rclone.conf copy --s3-chunk-size=20M docurba_exports:/docurba-exports exports/

move_exports_from_outscale:
	cd django && direnv exec . rclone --config scripts/rclone.conf move --s3-chunk-size=20M docurba_exports:/docurba-exports exports/

delete_silk_files:
	find -name "*.prof" -delete
