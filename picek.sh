#!/bin/bash

echo "Sarting..."
DIR=./configs/*
echo "Found $(ls -l $DIR | grep .ini | wc -l) config files"
echo "processing..."
for file in $DIR; do
    if [[ $file == *.ini ]] ; then
        echo "Executing program with config: $file"
        nice -19 nohup python3 main.py $file &
        sleep 2
        echo $file $! >> pid.txt
    else
        echo "Wrong config file: $file"
    fi
done