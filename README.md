## Running

1. Run `docker compose up -d`
2. Copy the spark script inside the `data` directory
3. Run the following
```bash
docker compose exec spark-master spark-submit --master spark://spark-master:7077 /spark_data/test.py
```
