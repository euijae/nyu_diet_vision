import os
from datasets import load_dataset
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image
import numpy as np
import logging


def init():
    global labels, device, model, processor, label_tokens
    
    imagenette = load_dataset('food101')
    model_id = "openai/clip-vit-base-patch32"
    
    labels = imagenette['train'].features['label'].names
    clip_labels = [f"a photo of a {label}" for label in labels]
    
    processor = CLIPProcessor.from_pretrained(model_id)
    model = CLIPModel.from_pretrained(model_id)
    
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    
    # create label tokens
    label_tokens = processor(
        text=clip_labels,
        padding=True,
        images=None,
        return_tensors='pt'
    ).to(device)
    
def classify_food(image_path):
    # encode tokens to sentence embeddings
    label_emb = model.get_text_features(**label_tokens)

    # detach from pytorch gradient computation
    label_emb = label_emb.detach().cpu().numpy()
    label_emb.min(), label_emb.max()

    # normalization
    label_emb = label_emb / np.linalg.norm(label_emb, axis=0)
    label_emb.min(), label_emb.max()

    # creating a object
    # path = imagenette['train'][15001]['image']
    # im = Image.open(path)
    HOME = os.getcwd()  # /Users/EKim45/Projects/euijae_project/diet_vision

    path = os.path.join(HOME, "images", image_path)  # torch.Size([1, 3, 224, 224])
    image = processor(
        text=None,
        images=Image.open(path),
        return_tensors='pt'
    )['pixel_values'].to(device)

    img_emb = model.get_image_features(image)
    img_emb = img_emb.detach().cpu().numpy()
    scores = np.dot(img_emb, label_emb.T)
    pred = np.argmax(scores)

    logging.debug(scores)
    logging.debug(pred)
    logging.debug(labels[pred])
    
init()
classify_food('chocolate_cake.jpg')