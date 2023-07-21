import os
import torch
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import cv2
import numpy as np
from PIL import Image
import supervision as sv
from matplotlib import pyplot as plt
import random
from pathlib import Path


class DietVision:

    def __init__(self) -> None:
        """
        """
        self.HOME = Path(__file__).parent.parent.absolute() / "static"
        
        CHECKPOINT_PATH = os.path.join(self.HOME, "weights", "sam_vit_h_4b8939.pth")
        DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        MODEL_TYPE = 'vit_h'

        sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=DEVICE)
        self.mask_generator = SamAutomaticMaskGenerator(sam)

    def upload_image(self):
        """
        TODO 
            an image must be coming through frontend and uploaded by an user
            validation of an image done in frontend
        """
        image_name = 'fish_chips.jpg'
        self.image_directory = os.path.join(self.HOME, 'images')
        
        self.image_path = os.path.join(self.image_directory, image_name)
        self.image_brg = cv2.imread(self.image_path) # np.ndarray
        self.original_image = cv2.cvtColor(self.image_brg, cv2.COLOR_BGR2RGB) # np.ndarray
        self.sam_result = self.mask_generator.generate(self.original_image)

        self._init_masks()
        self._init_mask_dictionary()
        self._init_diet_vision_dictionary()

    def _init_masks(self):
        mask_annotator = sv.MaskAnnotator()
        detections = sv.Detections.from_sam(sam_result=self.sam_result)

        self.annotated_image = mask_annotator.annotate(scene=self.image_brg.copy(), detections=detections)
        self.masks = [mask['segmentation'] for mask in sorted(self.sam_result, key=lambda x: x['area'], reverse=True)]

    def _init_diet_vision_dictionary(self):
        diet_vision_data = [{
            'mask': mask['segmentation'],
            'area': mask['area'],
            'class': None,
            'redirect': -1,
        } for mask in sorted(self.sam_result, key=lambda x: x['area'], reverse=True)]

        self.diet_vision_dictionary = {}
        for idx, m in enumerate(diet_vision_data):
            self.diet_vision_dictionary.update({ idx: m })

    def _init_mask_dictionary(self):
        self.height, self.weight = self.masks[0].shape
        self.mask_dictionary = np.full((self.height, self.weight), -1)
        
        for mi in range(len(self.masks)):
            mask = self.masks[mi]
            for row in range(self.height): # y
                for col in range(self.weight): # x
                    if mask[row][col]:
                        if self.mask_dictionary[row][col] == -1:
                            self.mask_dictionary[row][col] = mi

    def create_overlay_image(self, points: list):
        indices = self._find_mask_indices(points)
        transparent_image_test = cv2.imread('../apps/images/blank_transparent_image.png')
        annotated_mask_test = self._spot_annotator_on_mask(indices)

        img1_test = Image.fromarray(transparent_image_test).convert('RGBA')
        img2_test = Image.fromarray(annotated_mask_test).convert('RGBA')

        img_test_new_data = []

        for item in img2_test.getdata():
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                img_test_new_data.append((255, 255, 255, 0))
            else:
                a, b, c, _ = item
                img_test_new_data.append((a, b, c, 127))

        # print(np.array(img_test_new_data).shape)
        img1_test.putdata(img_test_new_data)
        # TODO either save image or np.ndarray
        img1_test.save('../apps/images/test_test.png', "PNG")

    def _spot_annotator_on_mask(self, indices: list) -> np.ndarray:
        cp = sv.ColorPalette.default()
        idx = random.choice(range(len(cp.colors)))

        transparent_image_name = 'blank_transparent_image.png'
        transparent_image_name = os.path.join(self.image_directory, transparent_image_name)
        transparent_image = cv2.imread(transparent_image_name)
        transparent_image_copy = transparent_image.copy()
        colored_mask = np.zeros_like(transparent_image_copy, dtype=np.uint8)
        colored_mask[:] = cp.by_idx(idx).as_bgr()

        opacity: float = 0.5
        
        combined_masks = self._combine_masks(indices)

        return np.where(
            np.expand_dims(combined_masks, axis=-1),
            np.uint8(opacity*colored_mask + (1-opacity)*transparent_image_copy), 
            transparent_image_copy,
        )

    def _find_mask_indices(points: list) -> list:
        pass

    def _combine_masks(self, indices: list) -> np.ndarray:
        pass