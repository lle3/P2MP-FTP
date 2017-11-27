#!/bin/bash

SERVERS=("one" "two" "three")
FILE="file.txt"
MSS=100


# TASK 2

for i in `seq 1 10`;
do
    result=0
    for j in `seq 1 5`;
    do
        SECONDS=0
        python ./p2mpclient ${SERVERS[*]} 7735 $FILE $MSS
        ((result+=$SECONDS))
    done
    echo $(( result / 5 )) > task_2_mss_$MSS.txt
    (( MSS+=100 ))
done

