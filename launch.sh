#!/bin/bash

set -e


function launch_services(){
  for service in ./services/*
    do
        echo "launching ${service}"
        docker-compose -f "${service}/docker-compose.yaml" up -d --build
    done
}

function launch_turl_and_pg_sink() {
    echo "launching turl and turl sink"
    docker-compose -f docker-compose-run.yaml up -d --build
}


function launch_main()
{
    launch_services
    launch_turl_and_pg_sink
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]
then
    launch_main
fi
