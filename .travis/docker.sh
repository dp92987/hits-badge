#!/bin/bash

set -ev

APP=$1
ENV=$2
USER=$3
DOCKER_IMAGE=$4

if [ $ENV == production ]; then
  PORT=8001
  WORKERS=5
elif [ $ENV == development ]; then
  PORT=8002
  WORKERS=1
fi

docker pull $DOCKER_IMAGE

CONTAINER_ID=$(docker ps -aqf "name=${APP}_$ENV")

if ! [ -z $CONTAINER_ID ]; then
  docker stop $CONTAINER_ID
  docker rm $CONTAINER_ID
fi

docker run --detach --name ${APP}_$ENV --env FLASK_ENV=$ENV --env WORKERS=$WORKERS --restart=always --publish 127.0.0.1:$PORT:5000 --volume /home/$USER/.$APP:/usr/$APP/instance $DOCKER_IMAGE

docker system prune -f
