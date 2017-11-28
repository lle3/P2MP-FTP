#!/bin/bash

SERVERS=("18.221.133.82" "18.217.96.4" "18.216.98.166" "13.58.28.214" "18.217.86.137")
FILE="file.txt"
MSS=500


# TASK 1

for i in `seq 1 5`;
do
    result=0
    for j in `seq 1 5`;
    do
        SECONDS=0
        python ./p2mpclient.py ${SERVERS[@]:0:$i} 7735 $FILE $MSS
        ((result+=$SECONDS))
    done
    echo $(( result / 5 )) > task_1_nodes_$i.txt
done



