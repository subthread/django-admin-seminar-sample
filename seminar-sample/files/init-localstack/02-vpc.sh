#!/usr/bin/env bash

project_name=seminar-sample-local

security_group_ids=`aws ec2 describe-security-groups --query "SecurityGroups[].GroupId" | jq -r ". | @tsv"`
aws ec2 create-tags --resources ${security_group_ids} --tags "Key=Name,Value=${project_name}-vpc-default-sg"

subnet_ids=`aws ec2 describe-subnets --query "Subnets[].SubnetId" | jq -r ". | @tsv"`
aws ec2 create-tags --resources ${subnet_ids} --tags "Key=Name,Value=${project_name}-lambda-1a"
