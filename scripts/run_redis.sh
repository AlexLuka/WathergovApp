#!/bin/bash

docker run -d \
    --name redis-stack \
    -p 6379:6379 \
    -p 8001:8001 \
    -e REDIS_ARGS="--requirepass ${REDIS_PASS}" \
    redis/redis-stack:latest
