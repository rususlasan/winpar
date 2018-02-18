#!/bin/bash
# kill all process related to the program
kill -9 $(pidof geckodriver)
kill -9 $(pidof firefox)
kill -9 $(pidof python3)
