from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import BinaryType
import cv2
import numpy as np

# Initialize Spark session
spark = SparkSession.builder.appName("PDIGrayscaleImage").getOrCreate()

# Define a UDF to convert images to grayscale
def to_grayscale(image_bytes):
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    # Decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Convert image to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Encode image back to bytes
    _, buffer = cv2.imencode('.png', gray_img)
    return buffer.tobytes()

# Register the UDF with Spark
to_grayscale_udf = udf(to_grayscale, BinaryType())

# Load your images into a DataFrame (example uses images stored in a directory)
# Assuming the DataFrame has a binary column 'image' containing the image data
images_df = spark.read.format("binaryFile").load("/spark_data/Figure_1.png").selectExpr("content as image")

# Apply the grayscale UDF to the DataFrame
grayscale_images_df = images_df.withColumn("grayscale_image", to_grayscale_udf("image"))

# Collect and save the results if necessary
results = grayscale_images_df.collect()
for row in results:
    with open("/spark_data/grayscale_image.png", "wb") as f:
        f.write(row["grayscale_image"])

# Stop the Spark session
spark.stop()
