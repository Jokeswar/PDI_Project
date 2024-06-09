#!/bin/bash

sudo cp test.py ./data/test.py
docker compose exec spark-master spark-submit --master spark://spark-master:7077 /spark_data/test.py
