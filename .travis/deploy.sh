#!/bin/bash

set -e

HOST=$1
USER=$2
PASSWORD=$3
DOCKER_IMAGE=$4

scp .travis/docker.sh $USER@$HOST:/tmp
echo $PASSWORD | ssh -tt $USER@$HOST "/tmp/docker.sh $APP $USER $DOCKER_IMAGE" && EXIT_CODE=$(echo $?) || EXIT_CODE=$(echo $?)
ssh $USER@$HOST "rm /tmp/docker.sh"

exit $EXIT_CODE
