APP_NAME := $(lastword $(subst /, ,$(abspath $(dir $(lastword $(MAKEFILE_LIST))))))
FIXTURES_PATH = files/fixtures

docker_name := $(lastword $(subst /, ,$(abspath $(dir $(lastword $(MAKEFILE_LIST))))))
branch := `git branch | grep '*' | sed -e 's/* //'`

ifeq (${environment},develop)
	override short_environment := dev
else ifeq (${environment},accept)
	override short_environment := stg
else ifeq (${environment},production)
	override short_environment := prd
else
	override short_environment := local
endif
override project_name := seminar-sample-${short_environment}


# デフォルトアクション
.PHONY: run up logs full-logs stop down
run: up update
	@docker compose logs -f ; docker compose down

up: setup
	docker compose up -d

logs:
	@docker compose logs -f server

full-logs:
	@docker compose logs -f

stop:
	docker compose stop

down:
	docker compose down


### setup ###

.PHONY: setup initialize setup-groups
setup: files/local.py .env

initialize: setup clean up update \
	$(patsubst %.json,%.loaded,$(sort $(wildcard ${FIXTURES_PATH}/*.json))) \
	setup-groups run

setup-groups:
	docker compose exec server python src/manage.py setupgroups

# files/local.py が無いか、files/local.default.py が更新されていたとき
files/local.py: files/local.default.py
	@if test ! -f $@; then cp $< $@; echo "$@ created"; fi
	@if test $< -nt $@; then echo "$< が更新されています！ $@ を削除するか編集してください"; exit 1; fi

.env: default.env
	@if test ! -f $@; then cp $< $@; echo "$@ created"; fi
	@if test $< -nt $@; then echo "$< が更新されています！ $@ を削除するか編集してください"; exit 1; fi

%.loaded: %.json
	docker compose exec -T server python src/manage.py loaddata --format json - < $<
	@touch $@


### update系 ###

.PHONY: update update-postgres update-server update-redis

update: update-postgres update-server update-redis

update-postgres:
	docker compose exec server python src/manage.py migrate --database=default

update-server:
	docker compose exec server python src/manage.py collectstatic --no-input

update-redis:


### clean系 ###

.PHONY: full-clean clean clean-postgres clean-redis clean-localstack clean-server

full-clean: clean
	-@rm -f .env files/local.py

clean: down clean-postgres clean-redis clean-localstack clean-server
	-@rm -f ${FIXTURES_PATH}/*.loaded

clean-postgres:
	$(eval database_volume = $(shell docker volume ls | grep -i "${APP_NAME}[_-]database-data" | awk '{print $$2}'))
	@if test "${database_volume}" != ""; then docker volume rm ${database_volume}; fi

clean-redis:
	$(eval session_volume = $(shell docker volume ls | grep -i "${APP_NAME}[_-]session-data" | awk '{print $$2}'))
	@if test "${session_volume}" != ""; then docker volume rm ${session_volume}; fi

clean-localstack:

clean-server:
	$(eval server_image = $(shell docker image ls | grep -i "${APP_NAME}[_-]server" | awk '{print $$1}'))
	@if test "${server_image}" != ""; then docker image rm ${server_image}; fi


### 管理系 ###

.PHONY: shell dbshell localstack makemigrations backup

shell:
	docker compose exec server python src/manage.py shell

dbshell:
	docker compose exec postgres psql -U postgres application_db

localstack:
	docker compose exec localstack bash

makemigrations:
	docker compose exec server python src/manage.py makemigrations

backup:
	docker compose exec localstack awslocal s3 sync s3://resource-bucket/ /etc/localstack/init/ready.d/init-files/
