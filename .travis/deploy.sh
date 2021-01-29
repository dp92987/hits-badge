#!/bin/bash

set -ev

ENV=$1
HOST=$2
USER=$3
PASSWORD=$4
DOCKER_IMAGE=$5

scp .travis/docker.sh $USER@$HOST:/tmp
echo $PASSWORD | ssh -tt $USER@$HOST "/tmp/docker.sh $APP $ENV $USER $DOCKER_IMAGE" && EXIT_CODE=$(echo $?) || EXIT_CODE=$(echo $?)
ssh $USER@$HOST "rm /tmp/docker.sh"

exit $EXIT_CODE
