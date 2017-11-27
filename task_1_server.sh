#!/bin/bash

PROB=0.05

for i in `seq 1 5`;
do
    for j in `seq 1 5`;
    do
        python3 ./p2mpserver 7735 test.txt $PROB >> task_1.log
    done
done

