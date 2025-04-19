#!/bin/bash

APP="ccmorph-ctc"
OFF='\033[0m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m' 

source env/bin/activate

docker stop "$APP"
docker rm "$APP"
# not necessary
docker image rm -f "$APP"

