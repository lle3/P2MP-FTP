#!/bin/bash

PROB=0.05
while [ 1 ]
do
    python3 ./p2mpserver.py 7735 test.txt $PROB >> task_1.log
done
