#!/bin/bash

SERVERS=("18.216.98.166" "13.58.28.214" "18.217.86.137")
FILE="file.txt"
MSS=500


# TASK 3

for i in `seq 1 10`;
do
    SECONDS=0
    python ./p2mpclient.py ${SERVERS[*]} 7737 $FILE $MSS
    echo $SECONDS > task_3_prob_$i.txt
done



