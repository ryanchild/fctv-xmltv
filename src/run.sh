#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

mkdir -p $DIR/data
rm -rf $DIR/fctv.xml

while true; do
    echo "downloading today's guide data"
    if python $DIR/fctv_guide.py; then
        mv $DIR/fctv.xml $DIR/data/
        echo "done"
    fi
    # guide is only available for today and seems to be posted some time between midnight and 3am?  so check every 3 hours
    sleep 10800
done