#!/usr/bin/env bash

# create bucket
bucket_name="resource-bucket"
awslocal s3 ls | grep ${bucket_name} > /dev/null
if [ $? -ne 0 ]; then
  awslocal s3 mb s3://${bucket_name}
fi

# file upload
awslocal s3 sync `dirname $0`/init-files s3://${bucket_name}/
