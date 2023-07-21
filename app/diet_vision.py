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
from datasets import load_dataset
from transformers import CLIPProcessor, CLIPModel
import calendar
import datetime


class DietVision:

    def __init__(self) -> None:
        """
        """
        home_posix = Path(__file__).parent.parent.absolute() / "static"
        self.test_value = 'test1'
        self.HOME = str(home_posix.as_posix())
        CHECKPOINT_PATH = os.path.join(self.HOME, "weights", "sam_vit_h_4b8939.pth")
        self.DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        MODEL_TYPE = 'vit_h'

        sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=self.DEVICE)
        self.mask_generator = SamAutomaticMaskGenerator(sam)
        self._init_image_classification()

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
        self._generate_blank_transparent_image()

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

    def _generate_blank_transparent_image(self):
        transparent_image_file_name = 'blank_transparent_image.png'
        self.blank_transparent_image_path = os.path.join(self.HOME, 'images', transparent_image_file_name)

    def create_overlay_image(self, indices: list) -> str:
        transparent_image_test = cv2.imread(self.blank_transparent_image_path)
        transparent_image_test = transparent_image_test.copy()
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

        date = datetime.datetime.utcnow()
        utc_time = str(calendar.timegm(date.utctimetuple()))

        overlay_image_path = os.path.join(self.HOME, 'images', f'overlay_image_{utc_time}.png')
        
        img1_test.putdata(img_test_new_data)        
        img1_test.save(overlay_image_path, "PNG")

        return overlay_image_path

    def _spot_annotator_on_mask(self, indices: list) -> np.ndarray:
        cp = sv.ColorPalette.default()
        idx = random.choice(range(len(cp.colors)))

        transparent_image = cv2.imread(self.blank_transparent_image_path)
        transparent_image = transparent_image.copy()
        colored_mask = np.zeros_like(transparent_image, dtype=np.uint8)
        colored_mask[:] = cp.by_idx(idx).as_bgr()

        opacity2: float = 0.5
        
        combined_masks = self._combine_masks(indices)

        return np.where(
            np.expand_dims(combined_masks, axis=-1),
            np.uint8(opacity2*colored_mask + (1 - opacity2) * transparent_image), 
            transparent_image,
        )

    def find_mask_indices(self, bbox_plot: list) -> list:
        x1, y1, x2, y2 = bbox_plot

        index_set = set()

        for row in range(y1, y2+1):
            for col in range(x1, x2+1):
                curr_mask_index = self.mask_dictionary[row][col]
                if curr_mask_index > -1 and not curr_mask_index in index_set:
                    index_set.add(curr_mask_index)

        index_list = list(index_set)
        index_list.sort()

        return index_list

    def _combine_masks(self, index_list: list) -> np.ndarray:
        i0 = index_list[0]
        combined_mask = self.diet_vision_dictionary[i0]['mask'].copy()

        for idx in index_list[1:]:
            curr_mask = self.diet_vision_dictionary[idx]['mask'].copy()
            combined_mask = np.logical_or(combined_mask, curr_mask)

        return combined_mask
    
    def _init_image_classification(self):
        imagenette = load_dataset('food101')
        self.labels = imagenette['train'].features['label'].names

        # generate sentences
        self.clip_labels = [f"a photo of a {label}" for label in self.labels]
        model_id = "openai/clip-vit-base-patch32"

        self.processor = CLIPProcessor.from_pretrained(model_id)
        self.model = CLIPModel.from_pretrained(model_id)

    def _food_classification(self, image_ndarray: np.ndarray) -> any:
        # create label tokens
        label_tokens = self.processor(
            text=self.clip_labels,
            padding=True,
            images=None,
            return_tensors='pt'
        ).to(self.DEVICE)

        # encode tokens to sentence embeddings
        label_emb = self.model.to(self.DEVICE).get_text_features(**label_tokens)

        # detach from pytorch gradient computation
        label_emb = label_emb.detach().cpu().numpy()

        # normalization
        label_emb = label_emb / np.linalg.norm(label_emb, axis=0)

        image = self.processor(
            text=None,
            images=Image.fromarray(image_ndarray),
            return_tensors='pt'
        )['pixel_values'].to(self.DEVICE)

        img_emb = self.model.get_image_features(image)
        img_emb = img_emb.detach().cpu().numpy()
        scores = np.dot(img_emb, label_emb.T)
        pred = np.argmax(scores)

        return self.labels[pred]
    
    def _generate_imagearray_from_mask(self, mask_by_sam) -> np.ndarray:
        """
        """
        original_image = cv2.imread(self.image_path)
        original_image = original_image.copy()
        mask = np.repeat(mask_by_sam[:, :, np.newaxis], 3, axis=2).copy() 
        filled_mask = np.where(mask, np.uint8(original_image), mask)

        return cv2.cvtColor(filled_mask, cv2.COLOR_BGR2RGB)
    
    def get_data_by_mask_index(self, mask_index) -> any:
        dict_data = self.diet_vision_dictionary[mask_index]
        mask_at_given_index = dict_data['mask']
        food_array = self._generate_imagearray_from_mask(mask_at_given_index)
        food_class = self._food_classification(food_array)
        
        dict_data.update({ 'class': food_class })

        return dict_data['class'], dict_data['area']