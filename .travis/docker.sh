#!/bin/bash

set -ev

APP=$1
USER=$2
DOCKER_IMAGE=$3

CONTAINER_ID=$(sudo docker ps | grep $APP | cut -d" " -f1)

sudo docker pull $DOCKER_IMAGE

if [ ! -z "$CONTAINER_ID" ]; then
  sudo docker stop $CONTAINER_ID
fi

sudo docker run -d --restart=always -p 127.0.0.1:8001:8001 -v /home/$USER/.$APP:/usr/$APP/instance $DOCKER_IMAGE

sudo docker system prune -f
