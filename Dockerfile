# 选择基础镜像
FROM nvidia/cuda:11.3.0-cudnn8-runtime-ubuntu20.04

# 以root用户身份运行所有命令
USER root

# 安装软件源及Python 3.10
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip && \
    ln -s /usr/bin/python3.10 /usr/bin/python

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 克隆FAME-ViL项目
RUN git clone https://github.com/BenjaminPang/FAME-ViL.git
WORKDIR /FAME-ViL

# 安装FAME-ViL项目的依赖
RUN pip install -e .
RUN pip install -r requirements.txt

# 安装PyTorch和torchvision
RUN pip install torch==1.12.0+cu113 torchvision==0.13.0+cu113 torchaudio==0.12.0 --extra-index-url https://download.pytorch.org/whl/cu113

# 设置环境变量
ENV WANDB_API_KEY=13a431a3eec762cf4f2029a64a6078788baf7252

# 设置容器的默认命令为bash
CMD ["bash"]