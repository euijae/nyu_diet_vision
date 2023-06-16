import os
import cv2
import supervision as sv
import torch
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor


HOME = os.getcwd()
print(HOME)

CHECKPOINT_PATH = os.path.join(HOME, "apps", "weights", "sam_vit_h_4b8939.pth")
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
MODEL_TYPE = "vit_h"
sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=DEVICE)
mask_generator = SamAutomaticMaskGenerator(sam)

IMAGE_NAME = 'fish_chips.jpg'
IMAGE_PATH = os.path.join(HOME, "apps", "images", IMAGE_NAME)
image_bgr = cv2.imread(IMAGE_PATH)
image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

sam_result = mask_generator.generate(image_rgb)

mask_annotator = sv.MaskAnnotator()

detections = sv.Detections.from_sam(sam_result=sam_result)

annotated_image = mask_annotator.annotate(scene=image_bgr.copy(), detections=detections)

sv.plot_images_grid(
    images = [image_bgr, annotated_image],
    grid_size = (1, 2),
    titles = ['source image', 'segmented image']
)

masks = [
    mask['segmentation']
    for mask
    in sorted(sam_result, key=lambda x: x['area'], reverse=True)
]

print(type(annotated_image))
