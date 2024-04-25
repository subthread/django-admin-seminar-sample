#!/usr/bin/env bash

secret_name=xxx
secret=`jq -nc --arg username ${POSTGRES_USER} --arg password ${POSTGRES_PASSWORD} '{"username":$username,"password":$password}'`

aws secretsmanager create-secret --name ${secret_name} --secret-string ${secret}
aws ssm put-parameter --name /seminar-sample-local/database/host --value ${DATABASE_HOST} --type String
aws ssm put-parameter --name /seminar-sample-local/database/name --value ${POSTGRES_DB} --type String
aws ssm put-parameter --name /seminar-sample-local/database/secret-name --value ${secret_name} --type SecureString

secret_name=zzz
secret=`jq -nc --arg user "${EMAIL_HOST_USER}" --arg password "${EMAIL_HOST_PASSWORD}" '{"user":$user,"password":$password}'`

aws secretsmanager create-secret --name ${secret_name} --secret-string ${secret}
aws ssm put-parameter --name /seminar-sample-local/email/host --value ${EMAIL_HOST} --type String
aws ssm put-parameter --name /seminar-sample-local/email/port --value ${EMAIL_PORT} --type String
aws ssm put-parameter --name /seminar-sample-local/email/secret-name --value ${secret_name} --type SecureString
aws ssm put-parameter --name /seminar-sample-local/email/from --value ${EMAIL_FROM} --type String
aws ssm put-parameter --name /seminar-sample-local/email/bucket --value ${IMPORT_STORAGE_BUCKET} --type String
