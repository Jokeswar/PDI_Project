#!/bin/bash

sudo cp test.py ./data/test.py
docker compose exec spark-master spark-submit --executor-memory 3g --driver-memory 3g --master spark://spark-master:7077 /spark_data/test.py
