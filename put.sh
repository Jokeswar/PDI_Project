#!/bin/bash

FILE="$1"

sudo cp "$FILE" ./hadoop_data/
docker exec -it namenode hdfs dfs -put -f /mnt/data/"$(basename "$FILE")" /user/spark/input
