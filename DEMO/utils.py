import cv2
import os
import time
import torch
from torchvision import transforms
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, GPT2Tokenizer, GPT2LMHeadModel
from clipcap import ClipCaptionModel
import clip
from gtts import gTTS

def speak(text, frame_count):
    # 변환할 텍스트
    text = "안녕하세요, 이것은 gTTS를 이용한 예시입니다."

    # TTS 객체 생성 (언어는 'ko'로 설정)
    tts = gTTS(text=text, lang='ko')

    # 음성 파일 저장 폴더
    save_dir = "./voices"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 음성 파일 저장
    filename = os.path.join(save_dir, f"mp3_{frame_count}.mp3") # 프레임 번호에 따른 음성 생성
    tts.save(filename)

    # 저장된 음성 파일 재생 (플랫폼에 따라 다를 수 있음)
    os.system(f"start {filename}")  # Windows에서는 'start', macOS에서는 'afplay', Linux에서는 'mpg321' 명령을 사용

def clip_load():
    # CLIP 모델 및 프로세서 로드
    # load clip
    device = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model, preprocess = clip.load("ViT-B/32", device=device, jit=False)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    prefix_length = 10
    return clip_model, preprocess, tokenizer, prefix_length

def clipcap_load():
    # load ClipCap
    device = "cuda" if torch.cuda.is_available() else "cpu"
    clip_model, preprocess, tokenizer, prefix_length = clip_load()
    model_path = "./checkpoints/pytorch_model.pt"
    model = ClipCaptionModel(prefix_length, tokenizer=tokenizer)
    model.from_pretrained(model_path)
    model = model.eval()
    model = model.to(device)

    return clip_model, model, preprocess, prefix_length

# 이미지 로드 및 전처리
def load_image(image_path):
    # 이미지 로드 : 원하는 이미지로 바꿀 수 있어요
    # url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    # image = Image.open(requests.get(url, stream=True).raw)
    image = Image.open(image_path).convert('RGB')
    return image

# 이미지에서 특징 추출
def extract_image_features(image_path, logger):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    start = time.time()
    clip_model, clipcap_model, preprocess, prefix_length = clipcap_load()
    
    # extract the prefix
    image = load_image(image_path)
    image = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        prefix = clip_model.encode_image(image).to(
            device, dtype=torch.float32
        )
        prefix_embed = clipcap_model.clip_project(prefix).reshape(1, prefix_length, -1)

    end = time.time()
    process_time = end - start
    logger.info(f"사진의 임베딩을 구하는데 걸린 시간 : {process_time:.4f}초")
    return clipcap_model, prefix_embed

def generate_text(clipcap_model, prefix_embed):
    # generate the caption
    text = clipcap_model.generate_beam(embed=prefix_embed)[0]
    return text

# 구분선 함수
def log_separator(logger):
    logger.info("-" * 50)