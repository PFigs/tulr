#!/bin/bash

set -e

source ./launch.sh


function run_tests()
{
    docker-compose up --build --abort-on-container-exit --exit-code-from turl
}

function test_main()
{
    docker network create turl-services-network || true
    launch_services
    run_tests
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]
then
    test_main
fi
