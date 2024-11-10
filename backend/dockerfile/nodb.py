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

app = FastAPI()

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

        return {"caption": caption}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect/")
async def detect_objects(file: UploadFile = File(...)):
    """YOLO 모델로 객체 탐지를 수행합니다."""
    try:
        # 이미지 로드
        image_data = await file.read()
        raw_image = Image.open(BytesIO(image_data)).convert("RGB")
        frame = np.array(raw_image)

        # YOLO 모델로 추론
        results = yolo_model.track(frame, persist=True)
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
        else:
            boxes = []
            track_ids = []

        # 결과 프레임에 추적 선 시각화
        annotated_frame = results[0].plot()
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            track = track_history[track_id]
            track.append((float(x), float(y)))  # 중심 좌표 추가
            if len(track) > 30:
                track.pop(0)

            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(
                annotated_frame,
                [points],
                isClosed=False,
                color=(230, 230, 230),
                thickness=10,
            )

        # 결과 이미지를 base64로 인코딩하여 반환
        _, encoded_image = cv2.imencode(".jpg", annotated_frame)
        base64_image = base64.b64encode(encoded_image).decode("utf-8")
        
        return {"detected_image": base64_image}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))