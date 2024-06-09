FROM bitnami/spark:latest

USER root

RUN apt update && \
    apt install libgl1 libglib2.0-0 -y && \
    pip3 install opencv-python
