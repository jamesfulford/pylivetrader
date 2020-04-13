#!/bin/bash

target_script="${1:-"algorithms/basic-algo.py"}"
config_file="${2:-"config/.env"}"

docker run --rm \
    -v $PWD:/work -w /work \
    --env-file "$config_file" \
    james-fulford/zipline \
    pylivetrader run -f "$target_script"
