#!/bin/bash

geck_pids=$(pidof geckodriver)

for i in $geck_pids;do
	kill -9 $i;
done

fire_pids=$(pidof firefox)

for i in $fire_pids;do
	kill -9 $i;
done
