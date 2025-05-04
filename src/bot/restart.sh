#!/bin/bash

bash stop.sh

#wait 5 seconds
sleep 2

git pull

sleep 2

bash start.sh
