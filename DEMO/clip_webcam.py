import streamlit as st
import cv2
import os
import time
import torch
from torchvision import transforms
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, GPT2Tokenizer, GPT2LMHeadModel
import requests

from datetime import datetime
import logging
# # CLIP 모델 및 프로세서 로드
# clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
# clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")

# # GPT-2 모델 및 토크나이저 로드
# gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
# gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

if not os.path.exists("./log"):
    os.makedirs("./log")

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 로거 설정
logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정
    format='%(message)s',  # 로그 출력 형식
    handlers=[
        logging.FileHandler("./log/app_{current_time}.log"),  # 로그를 파일로 저장 (파일명: app.log)
        logging.StreamHandler()  # 콘솔에도 출력
    ]
)

# 로거 가져오기
logger = logging.getLogger(__name__)

# 구분선 함수
def log_separator():
    logger.info("-" * 50)

def clip_load():
    # CLIP 모델 및 프로세서 로드
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch16")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
    return model, processor

# 이미지 로드 및 전처리
def load_image(image_path):
    # 이미지 로드 : 원하는 이미지로 바꿀 수 있어요
    # url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    # image = Image.open(requests.get(url, stream=True).raw)
    image = Image.open(image_path)
    return image

# 이미지에서 특징 추출
def extract_image_features(image_path):
    start = time.time()
    clip_model, clip_processor = clip_load()
    image = load_image(image_path)
    inputs = clip_processor(images=image, return_tensors="pt")

    with torch.no_grad():
        features = clip_model.get_image_features(**inputs)
    end = time.time()
    process_time = end - start
    logger.info(f"사진의 임베딩을 구하는데 걸린 시간 : {process_time:.4f}초")
    return features


# 프레임 저장 폴더
save_dir = "./frames"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Streamlit 페이지 구성
st.title("카메라 캡처 및 이미지 저장")

# 상태 변수
start_capture = st.button("카메라 시작")
stop_capture = st.button("카메라 종료")

# 옵션 선택: 1초 간격 또는 5프레임 간격
capture_interval = st.selectbox("이미지 저장 주기 선택", ["1초 간격", "5프레임 간격"])

# 카메라 캡처 시작
if start_capture:
    cap = cv2.VideoCapture(0)
    frame_count = 0  # 프레임 번호 카운팅
    last_saved_time = time.time()  # 마지막 저장 시간 기록
    
    st.write("카메라가 실행 중입니다. 이미지를 저장합니다...")

    # 스트리밍 및 저장 루프
    while True:
        ## logging
        logger.info(f"{frame_count}번째 턴:")
        turn_start = time.time()

        ## main process
        ret, frame = cap.read()
        if not ret:
            st.error("프레임을 가져올 수 없습니다.")
            break

        # 프레임을 보여주기 (Streamlit에서 OpenCV 사용 불가하므로 HTML로 전환)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, channels="RGB", caption="Camera Stream")

        # 이미지 저장 조건 체크
        if capture_interval == "1초 간격":
            if time.time() - last_saved_time >= 1:  # 1초 간격으로 저장
                filename = os.path.join(save_dir, f"frame_{frame_count}.jpg")

                frame_save_start = time.time()
                cv2.imwrite(filename, frame)
                st.write(f"{filename} 저장 완료")
                frame_save_end = time.time()
                frame_save_time = frame_save_end - frame_save_start
                logger.info(f"사진 저장에 걸린 시간: {frame_save_time}")

                frame_count += 1
                last_saved_time = time.time()

                # 방금 저장된 이미지에 대한 feature 추출
                feature = extract_image_features(filename)

        else:  # 5프레임 간격으로 저장
            if frame_count % 5 == 0:
                filename = os.path.join(save_dir, f"frame_{frame_count}.jpg")

                frame_save_start = time.time()
                cv2.imwrite(filename, frame)
                st.write(f"{filename} 저장 완료")
                frame_save_end = time.time()
                frame_save_time = frame_save_end - frame_save_start
                logger.info(f"사진 저장에 걸린 시간: {frame_save_time}")

                # 방금 저장된 이미지에 대한 feature 추출
                feature = extract_image_features(filename)

            frame_count += 1

        
        # time.sleep(2) # 저장 시간 지연에 따른 2초 추가
        # # 방금 저장된 이미지에 대한 feature 추출
        # feature = extract_image_features(filename)

        # '카메라 종료' 버튼이 눌리면 루프 종료
        if stop_capture:
            st.write("카메라 프로세스가 종료되었습니다.")
            break

        turn_end = time.time()
        turn_time = turn_end - turn_start
        logger.info(f"{frame_count-1}번째 턴 총 실행시간: {turn_time}")
        log_separator()

    cap.release()  # 카메라 해제
    cv2.destroyAllWindows()

elif stop_capture:
    st.write("카메라가 종료되었습니다.")
