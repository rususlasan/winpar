#!/bin/bash

# search and kill geckodriver and firefox PIDs

geck_pids=$(pidof geckodriver)
fire_pids=$(pidof firefox)

if [ -z $geck_pids ] && [ -z $fire_pids ]; then
    echo "There are no active geckodriver and firefox PIDs"
    exit 0
fi

echo "Found geckodriver PIDs: ${geck_pids} and firerfox PIDs: ${fire_pids}"

for i in $geck_pids;do
	kill -9 $i;
done

for i in $fire_pids;do
	kill -9 $i;
done
