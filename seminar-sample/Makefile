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

.PHONY: setup initialize setup-groups prepare-file
setup: files/local.py files/proxy.conf .env

initialize: setup clean up update \
	$(patsubst %.json,%.loaded,$(sort $(wildcard ${FIXTURES_PATH}/*.json))) \
	setup-groups run

setup-groups:
	docker compose exec server python src/manage.py setupgroups

prepare-file:
	@# ${target} が無ければ作る、${source} が更新されていたらエラーする
	@if test ! -f ${target}; then cp ${source} ${target}; echo "${target} created"; fi
	@if test ${source} -nt ${target}; then echo "${source} が更新されています！ ${target} を削除するか編集してください"; exit 1; fi

files/local.py: files/default.local.py
	@make prepare-file "source=$<" "target=$@"

files/proxy.conf: files/default.proxy.conf
	@make prepare-file "source=$<" "target=$@"

.env: default.env
	@make prepare-file "source=$<" "target=$@"

%.loaded: %.json
	docker compose exec -T server python src/manage.py loaddata --format json - < $<
	@touch $@


### Lambda ###

.PHONY: deploy-lambda deploy-logging-lambda deploy-mail-lambda lambda-log

deploy-lambda: deploy-logging-lambda deploy-mail-lambda

deploy-logging-lambda:
	@docker compose exec -w /lambda/logging localstack make deploy
	@make update-proxy

deploy-mail-lambda:
	@docker compose exec -w /lambda/recvmail localstack make deploy

recvmail:
	$(eval message_id := $(shell echo "test-mail-`date '+%s'`"))
	@if test "${target}" == ""; then echo "メールファイルを指定してください target=***"; exit 1; fi
	@if test ! -f "${target}"; then echo "メールファイル ${target} が見つかりません"; exit 1; fi
	@cp "${target}" ./lambda/${message_id}; \
		docker compose exec localstack aws s3 cp /lambda/${message_id} s3://import-bucket/; \
		rm ./lambda/${message_id}
	$(eval function_name := $(shell docker compose exec localstack \
		aws lambda list-functions --query 'Functions[?contains(FunctionName, `RecvMail`)].FunctionName' --output text))
	@# https://docs.aws.amazon.com/ses/latest/dg/receiving-email-action-lambda-event.html
	@docker compose exec localstack \
		aws lambda invoke /dev/stdout \
		--function-name "${function_name}" \
		--payload '{"Records": [{"ses":{"mail":{"messageId":"${message_id}"}}}]}'

lambda-log:
	$(eval log_group       := $(shell docker compose exec localstack aws logs describe-log-groups --output text --query 'logGroups[0].logGroupName'))
	$(eval log_stream_name := `docker compose exec localstack aws logs describe-log-streams --log-group-name '${log_group}' --order-by LastEventTime --output text --query 'logStreams[-1].logStreamName'`)
	@docker compose exec localstack aws logs get-log-events --log-group-name '${log_group}' --log-stream-name ${log_stream_name} --output text --query 'events[].[message]'


### update系 ###

.PHONY: update update-postgres update-redis update-localstack update-server update-proxy

update: update-postgres update-redis update-localstack update-server

update-postgres:
	docker compose exec server python src/manage.py migrate --database=default

update-redis:

update-localstack:

update-server:
	docker compose exec server python src/manage.py collectstatic --no-input

update-proxy:
	@# proxy.conf を書き換えて API Gateway にリクエストを送るようにする
	$(eval api_id := $(shell docker compose exec localstack aws apigateway get-rest-apis --query 'items[0].id' --output text))
	$(eval stage_name := $(shell docker compose exec localstack aws apigateway get-stages --rest-api-id ${api_id} --query 'item[0].stageName' --output text))
	@if test "${stage_name}" != ""; then \
		sed -i "" -e 's/set $$api_id .*/set $$api_id ${api_id};/' files/proxy.conf ;\
		sed -i "" -e 's/set $$stage_name .*/set $$stage_name ${stage_name};/' files/proxy.conf ;\
		docker compose restart proxy ;\
	fi
	@#docker compose exec proxy service nginx restart


### clean系 ###

.PHONY: full-clean clean clean-postgres clean-redis clean-localstack clean-server

full-clean: clean
	-@rm -f .env files/local.py files/proxy.conf

clean: down clean-postgres clean-redis clean-localstack clean-server
	-@rm -f ${FIXTURES_PATH}/*.loaded

clean-postgres:
	$(eval database_volume = $(shell docker volume ls | grep -i "${APP_NAME}[_-]database-data" | awk '{print $$2}'))
	@if test "${database_volume}" != ""; then docker volume rm ${database_volume}; fi

clean-redis:
	$(eval session_volume = $(shell docker volume ls | grep -i "${APP_NAME}[_-]session-data" | awk '{print $$2}'))
	@if test "${session_volume}" != ""; then docker volume rm ${session_volume}; fi

clean-localstack:
	$(eval localstack_image = $(shell docker image ls | grep -i "${APP_NAME}[_-]localstack" | awk '{print $$1}'))
	@if test "${localstack_image}" != ""; then docker image rm ${localstack_image}; fi
	-@rm -rf lambda/.aws-sam

clean-server:
	$(eval server_image = $(shell docker image ls | grep -i "${APP_NAME}[_-]server" | awk '{print $$1}'))
	@if test "${server_image}" != ""; then docker image rm ${server_image}; fi


### 管理系 ###

.PHONY: shell dbshell localstack makemigrations backup

shell:		# Django management shell を開く
	docker compose exec server python src/manage.py shell

dbshell:	# postgres の psql に接続する
	docker compose exec postgres sh -c "PGPASSWORD=\$$POSTGRES_PASSWORD psql -U postgres application_db"

localstack:	# localstack の bash に接続する
	docker compose exec localstack bash

makemigrations:
	docker compose exec server python src/manage.py makemigrations

backup:
	docker compose exec localstack awslocal s3 sync s3://resource-bucket/ /etc/localstack/init/ready.d/init-files/
