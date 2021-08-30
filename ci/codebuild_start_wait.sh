#!/bin/bash
set -eu -o pipefail

[[ $# -lt 2 ]] && {
    echo "Usage $0 <PROJECT_NAME> <S3_URL>" >&2
    echo "  Example: $0 project-name s3://mybucket/path" >&2
    exit 1
}

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
PROJECT_NAME=$1
S3_URL=$2

CB_ENV_OVERRIDE='[{"name":"TF_VAR_scan_s3_url","value":"'"$S3_URL"'","type":"PLAINTEXT"}]'

WAIT_INTERVAL=30 #in seconds

if [ -z $(aws codebuild list-projects  --output text --query "projects[? @ == '${PROJECT_NAME}']") ]; then
  echo "Codebuild command failed or project not found!"
  exit 1
else
  echo "Codebuild project found!  Starting build job..."
  BUILD_ID=$(aws codebuild start-build --project-name ${PROJECT_NAME} --environment-variables-override ${CB_ENV_OVERRIDE} --output text --query 'build.id')
fi

build_status() {
  aws codebuild batch-get-builds --ids ${BUILD_ID} --query 'builds[*].buildStatus' --output text
}

echo "Start checking status for build...(https://console.aws.amazon.com/codesuite/codebuild/$ACCOUNT_ID/projects/$PROJECT_NAME/build/$BUILD_ID/?region=$AWS_DEFAULT_REGION)"

while [ "$(build_status)" == "IN_PROGRESS" ]; do
  echo "[codebuild_start_wait]: Build is still in progress. Checking again in ${WAIT_INTERVAL} seconds..."
  sleep ${WAIT_INTERVAL}
done

if [ "$(build_status)" == "FAILED" ]; then
  echo "Build has FAILED"
  exit 1
fi

echo "Build completed successfully! (https://console.aws.amazon.com/codesuite/codebuild/$ACCOUNT_ID/projects/$PROJECT_NAME/build/$BUILD_ID/?region=$AWS_DEFAULT_REGION)"
exit 0
