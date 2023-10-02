#!/bin/sh

if [ $# -gt 0 ]; then
    exec "$@"
else
    tail -f /dev/null
fi