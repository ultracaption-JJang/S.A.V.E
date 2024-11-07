import os
import torch
import clip
from fastapi import FastAPI, UploadFile, File, HTTPException
from transformers import GPT2Tokenizer
from clipcap import ClipCaptionModel
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
from collections import defaultdict
import cv2
import numpy as np
import base64
import time
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

app = FastAPI()

# Database setup
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Caption(Base):
    __tablename__ = "captions"
    id = Column(Integer, primary_key=True, index=True)
    caption_text = Column(Text)
    processing_time = Column(String)

# class Detection(Base):
#     __tablename__ = "detections"
#     id = Column(Integer, primary_key=True, index=True)
#     detected_image_base64 = Column(Text)

Base.metadata.create_all(bind=engine)

# load pretrained model
def load_pretrained_model(model, pretrained_path):
    if os.path.isfile(pretrained_path):
        print(f"Loading pre-trained model from {pretrained_path}")
        model.load_state_dict(torch.load(pretrained_path, map_location=torch.device('cuda' if torch.cuda.is_available() else 'cpu')), strict=False)
        print("Model loaded successfully.")
    else:
        print(f"Pre-trained model file {pretrained_path} not found.")
    return model

model_path = "/app/clipcap/model_weights.pt"
# load clip
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device, jit=False)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
prefix_length = 10

# load ClipCap
model = ClipCaptionModel(prefix_length, tokenizer=tokenizer)
model = load_pretrained_model(model, model_path)
model = model.eval()
model = model.to(device)

# load YOLO
yolo_model = YOLO('yolo11n.pt')
track_history = defaultdict(lambda: [])


@app.post("/generate-caption/")
async def generate_caption(file: UploadFile = File(...)):
    start_time = time.time()
    db = SessionLocal()

    try:
        # Load the image
        image_data = await file.read() 
        raw_image = Image.open(BytesIO(image_data)).convert('RGB')

        # Extract the prefix
        image = preprocess(raw_image).unsqueeze(0).to(device)
        with torch.no_grad():
            prefix = clip_model.encode_image(image).to(device, dtype=torch.float32)
            prefix_embed = model.clip_project(prefix).reshape(1, prefix_length, -1)

        # Generate caption
        caption = model.generate_beam(embed=prefix_embed)[0]

        end_time = time.time()
        processing_time = end_time - start_time
        print(f'캡션 생성 소요 시간: {processing_time:.2f} seconds') # 처리시간 로그

        # Save caption to the database
        db_caption = Caption(caption_text=caption, processing_time=f"{processing_time:.2f} seconds")
        db.add(db_caption)
        db.commit()
        db.refresh(db_caption)

        return {"caption": caption}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/detect/")
async def detect_objects(file: UploadFile = File(...)):
    # db = SessionLocal()
    """YOLO 모델로 객체 탐지를 수행합니다."""
    try:
        # 이미지 로드
        image_data = await file.read()
        raw_image = Image.open(BytesIO(image_data)).convert("RGB")
        frame = np.array(raw_image)

        # YOLO 모델로 추론
        results = yolo_model.track(frame, persist=True)

        # results 객체에서 탐지된 객체 정보 가져오기
        detected_objects = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])  # 클래스 ID 가져오기
                object_name = result.names[class_id]  # 클래스 ID로부터 이름 가져오기
                confidence = box.conf[0]  # 신뢰도 가져오기
                coordinates = box.xyxy[0].tolist()  # 좌표 가져오기 (xmin, ymin, xmax, ymax)
    
                # 객체 정보를 딕셔너리 형태로 추가
                detected_objects.append({
                    "name": object_name,
                    "confidence": confidence,
                    "coordinates": coordinates
                })
        
        return {"detected_result": detected_objects}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))