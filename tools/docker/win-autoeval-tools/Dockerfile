#https://github.com/dusty-nv/jetson-containers
#FROM dustynv/l4t-pytorch:r36.2.0
FROM nvidia/cuda:12.3.1-runtime-ubuntu22.04
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN apt -y update && apt -y upgrade
RUN apt -y install python3 python3-pip git libopencv-dev
RUN apt -y update && apt -y upgrade
RUN ln -s /usr/bin/python3.10 /usr/bin/python
RUN pip install --upgrade pip
RUN pip install transformers Pillow torch torchvision torchaudio accelerate scipy jsonlines bitsandbytes
WORKDIR /app/tools
