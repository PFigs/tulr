#!/bin/bash

set -e

docker-compose build
docker-compose -f postgres/docker-compose.yaml build
