#!/bin/sh
cd /home/pi/thermopylae/

pgrep -a python | grep temp_regulator.py > /dev/null
if [ $? -eq 0 ]; then
    echo "Regulator is already running."
else
    python temp_regulator.py &
fi
pgrep -a python | grep server.py > /dev/null
if [ $? -eq 0 ]; then
    echo "Web server is already running."
else
    python server.py 2>flaskLog &
fi

