#!/bin/bash

target_script="${1:-"algorithms/basic-algo.py"}"
config_file="${2:-"config/.env"}"
daemon="${3:-"false"}"

optional_args=""

if [[ "false" != "$daemon" ]]; then
    optional_args="$optional_args -d"
fi

docker run --rm \
    -v $PWD:/work -w /work \
    --name pylivetrader \
    --env-file "$config_file" \
    $optional_args \
    jamespfulford/pylivetrader:latest \
    pylivetrader run -f "$target_script"
