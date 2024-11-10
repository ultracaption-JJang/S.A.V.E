# Base image
FROM amd64/python:3.10

# Set working directory
WORKDIR /app

# pip 업데이트 후에 fastapi설치
RUN pip install -U pip \
    && pip install "fastapi[all]" ultralytics opencv-python-headless pillow

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# COPY clipcap repository
COPY ../clipcap_dir /app/clipcap_dir

# COPY requirements file
COPY ../dockerfile/requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY ./dockerfile/main.py /app/main.py

# COPY ./dockerfile/main_0.py /app/main_0.py

# 환경 파일 복사
COPY ../dockerfile/.env /app/.env
COPY ../dockerfile/config.py /app/config.py  

# Command to run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
