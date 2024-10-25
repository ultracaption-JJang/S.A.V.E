import os
import torch
import clip
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from clipcap import ClipCaptionModel
import requests
from PIL import Image


# load pretrained model
def load_pretrained_model(model, pretrained_path):
    if os.path.isfile(pretrained_path):
        print(f"Loading pre-trained model from {pretrained_path}")
        # strict=False를 추가하여 일부 매개변수가 없어도 로딩 가능하도록 설정
        model.load_state_dict(torch.load(pretrained_path, map_location=torch.device('cuda' if torch.cuda.is_available() else 'cpu')), strict=False)
        print("Model loaded successfully.")
    else:
        print(f"Pre-trained model file {pretrained_path} not found.")
    return model

#model_path = "/Users/psjj/Downloads/coco_prefix-009.pt"  # change accordingly
#model_path = '/content/drive/MyDrive/MLB/NIPA/CLIP_prefix_caption_ViT-B_32_train_out/coco_prefix-099.pt'
model_path = '/content/drive/MyDrive/MLB/NIPA/CLIP_prefix_caption/model_wieghts.pt'
# load clip
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device, jit=False)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
prefix_length = 10

# load ClipCap
model = ClipCaptionModel(prefix_length, tokenizer=tokenizer)

# load the pretrained model weights
model = load_pretrained_model(model, model_path)
model = model.eval()
model = model.to(device)

# load the image
image_dir = '/content/drive/MyDrive/MLB/NIPA/CLIP_prefix_caption/Images/COCO_val2014_000000354533.jpg'
raw_image = Image.open(image_dir).convert('RGB')

# extract the prefix
image = preprocess(raw_image).unsqueeze(0).to(device)
with torch.no_grad():
    prefix = clip_model.encode_image(image).to(device, dtype=torch.float32)
    prefix_embed = model.clip_project(prefix).reshape(1, prefix_length, -1)

# assuming generate_beam() is correctly implemented in ClipCaptionModel
caption = model.generate_beam(embed=prefix_embed)[0]

print("Generated caption:", caption)
