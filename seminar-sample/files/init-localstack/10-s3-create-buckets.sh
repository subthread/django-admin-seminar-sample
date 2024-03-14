#!/usr/bin/env bash

function create_bucket {
  bucket_name=$1
  awslocal s3 ls | grep ${bucket_name} > /dev/null
  if [ $? -ne 0 ]; then
    awslocal s3 mb s3://${bucket_name}
  fi
}

create_bucket "resource-bucket"
create_bucket "archive-bucket"
create_bucket "import-bucket"
