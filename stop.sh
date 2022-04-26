#!/bin/bash

set -e


function stop_services(){
  for service in ./services/*
    do
        echo "stoping ${service}"
        docker-compose -f "${service}/docker-compose.yaml" down -v -t0
    done
}

function stop_turl_and_pg_sink() {
    echo "stoping turl and turl sink"
    docker-compose -f docker-compose-run.yaml down -v -t0
}


function stop_main()
{
    stop_services
    stop_turl_and_pg_sink
}


if [[ "${BASH_SOURCE[0]}" == "$0" ]]
then
    stop_main
fi
