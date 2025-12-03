#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <pid> <condition>"
    exit 1
fi

python -m evaluation_study.app --logpath "./evaluation_app.log" --pid "$1" --condition "$2" &

if [ $2 == "gesture" ]; then
    python -m main.app --logpath "./main_app.log" --nocampreview &
fi