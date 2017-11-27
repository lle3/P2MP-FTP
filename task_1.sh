#!/bin/bash

SERVERS=("18.217.114.37" "18.217.64.84" "52.15.69.135" "13.58.26.68" "18.217.111.251")
FILE="file.txt"
MSS=500


# TASK 1

for i in `seq 1 1`;
do
    result=0
    for j in `seq 1 1`;
    do
        SECONDS=0
        python ./p2mpclient.py ${SERVERS[@]:0:$i} 7735 $FILE $MSS
        ((result+=$SECONDS))
    done
    echo $(( result / 5 )) > task_1_nodes_$i.txt
done



