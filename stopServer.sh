#!/bin/sh
PID1=`pgrep -f temp_regulator.py`
if [ -z "$PID1" ]; then
   echo "Regulator not running."
else
    kill $PID1
fi
PID1=`pgrep -f server.py`
if [ -z "$PID1" ]; then
   echo "Web server not running."
else
    kill $PID1
fi
