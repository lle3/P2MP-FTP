#!/bin/bash

SERVERS=("one" "two" "three" "four" "five")
FILE="file.txt"
MSS=500


# TASK 1

for i in `seq 1 5`;
do
    result=0
    for j in `seq 1 5`;
    do
        SECONDS=0
        python ./p2mpclient ${SERVERS[@]:0:$i} 7735 $FILE $MSS
        ((result+=$SECONDS))
    done
    echo $(( result / 5 )) > task_1_nodes_$i.txt
done



