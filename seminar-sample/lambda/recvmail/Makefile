AWS_REGION ?= ap-northeast-1

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


.PHONY: build deoloy

build:
	@sam build

deploy: build
	$(eval secret_name := $(shell aws ssm get-parameter --with-decryption --name /${project_name}/email/secret-name --query Parameter.Value --output text))
	sam deploy \
		--stack-name recv-mail \
		--region ${AWS_REGION} \
		--capabilities CAPABILITY_NAMED_IAM \
		--parameter-overrides \
			ProjectName="${project_name}" \
			EMailHost="/${project_name}/email/host" \
			EMailPort="/${project_name}/email/port" \
			EMailFrom="/${project_name}/email/from" \
			S3Bucket="/${project_name}/email/bucket" \
			SecretName="${secret_name}" \
			VPCSecurityGroupIds="`make -s get-security-groups`" \
			VPCSubnetIds="`make -s get-subnets`" \
		--confirm-changeset

.PHONY: build deoloy get-security-groups get-subnets

get-security-groups:
	@aws ec2 describe-security-groups \
		--filter "Name=tag:Name,Values=${project_name}-vpc-default-sg,${project_name}-ecs-sg" \
		--query "SecurityGroups[].GroupId" \
		| jq -r ". | @csv" \
		| sed 's/"//g'

get-subnets:
	@aws ec2 describe-subnets \
		--filter "Name=tag:Name,Values=${project_name}-lambda-*" \
		--query "Subnets[].SubnetId" \
		| jq -r ". | @csv" \
		| sed 's/"//g'
