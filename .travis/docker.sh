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

sudo docker pull $DOCKER_IMAGE

CONTAINER_ID=$(sudo docker ps -aqf "name=$APP_ENV")

if ! [ -z $CONTAINER_ID ]; then
  sudo docker stop $CONTAINER_ID
  sudo docker rm $CONTAINER_ID
fi

sudo docker run --detach --name ${APP}_$ENV --env HITSBADGE_ENV=$ENV --restart=always --publish 127.0.0.1:$PORT:5000 --volume /home/$USER/.$APP:/usr/$APP/instance $DOCKER_IMAGE "--workers=$WORKERS"

sudo docker system prune -f
