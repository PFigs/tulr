#!/bin/bash
# shellcheck disable=SC1091

set -e

source ./launch.sh
source ./stop.sh


function run_tests()
{
    docker-compose up --build --abort-on-container-exit --exit-code-from turl
}

function test_main()
{
    docker network create turl-services-network || true
    launch_services
    run_tests
    stop_services
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]
then
    test_main
fi
