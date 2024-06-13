from pyspark.sql import SparkSession
import numpy as np
import cv2
from pyspark.sql.functions import udf
from pyspark.sql.types import BinaryType
from pyspark import SparkFiles

# Initialize Spark session
spark = SparkSession.builder.appName("PDI-Alb-Negru").getOrCreate()

# HDFS configuration
hdfs_url = "hdfs://namenode:9000"

# Read image from HDFS
image_path = f"{hdfs_url}/user/spark/input/sat_1.jpg"
spark.sparkContext.addFile(image_path)

# Function to convert an image to grayscale
def to_grayscale(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, buffer = cv2.imencode('.png', gray_img)
    return buffer.tobytes()

# Function to merge blocks into a single image
def merge_blocks(blocks):
    block_imgs = [cv2.imdecode(np.frombuffer(block, np.uint8), cv2.IMREAD_GRAYSCALE) for block in blocks]
    return cv2.vconcat(block_imgs)

# Register UDF
to_grayscale_udf = udf(to_grayscale, BinaryType())

# Read image as binary file
with open(SparkFiles.get(image_path.split('/')[-1]), "rb") as f:
    image_data = f.read()

# Split the image into blocks
def split_image(image_data, num_splits):
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    height, width, _ = img.shape
    block_height = height // num_splits
    blocks = []
    for i in range(num_splits):
        start_row = i * block_height
        end_row = (i + 1) * block_height if i != num_splits - 1 else height
        block = img[start_row:end_row, :, :]
        _, buffer = cv2.imencode('.png', block)
        blocks.append(buffer.tobytes())
    return blocks

num_splits = 256  # Number of splits
blocks = split_image(image_data, num_splits)

# Create an RDD from the blocks and process each block
rdd = spark.sparkContext.parallelize(blocks, numSlices=64)
print(f"Number of partitions: {rdd.getNumPartitions()}")
grayscale_rdd = rdd.map(to_grayscale)

# Collect and save the grayscale blocks to HDFS
grayscale_blocks = grayscale_rdd.collect()
merged_image = merge_blocks(grayscale_blocks)
_, buffer = cv2.imencode('.png', merged_image)
output_path = f"/spark_data/grayscale_image.png"
with open(output_path, "wb") as f:
   f.write(buffer.tobytes())

# Stop the Spark session
spark.stop()
