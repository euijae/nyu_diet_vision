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
        home_posix = Path(__file__).parent.parent.absolute() / "static"

        self.HOME = str(home_posix.as_posix())
        self.DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        CHECKPOINT_PATH = os.path.join(self.HOME, "weights", "sam_vit_h_4b8939.pth")
        MODEL_TYPE = 'vit_h'

        sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH).to(device=self.DEVICE)

        self.mask_generator = SamAutomaticMaskGenerator(sam)
        self._index_group_list = []
        self._overlay_image_stack = []
        self._maximum_image_stack_size = 5

    def _cleanup_image_stack(self) -> None:
        if len(self._overlay_image_stack) >= self._maximum_image_stack_size:
            for overlay_image_path in self._overlay_image_stack:
                os.system(f'rm {overlay_image_path}')

            self._overlay_image_stack.clear()

    def upload_image(self):
        self._init_image_classification()

        image_name = 'fish_chips.jpg'
        self.image_directory = os.path.join(self.HOME, 'images')
        
        self.image_path = os.path.join(self.image_directory, image_name)
        self.image_brg = cv2.imread(self.image_path) # np.ndarray
        self.original_image = cv2.cvtColor(self.image_brg, cv2.COLOR_BGR2RGB) # np.ndarray
        
        app_posix = Path(__file__).parent.parent.absolute() / "app"
        app_home = str(app_posix.as_posix())
        with open(f'{app_home}/sam_result.npy', 'rb') as f:
            self.sam_result = np.load(f, allow_pickle=True).copy()
            
        # self.sam_result = self.mask_generator.generate(self.original_image)

        self._init_diet_vision_dictionary()
        self._init_mask_dictionary()
        self._generate_blank_transparent_image()

    def _init_diet_vision_dictionary(self):
        self.diet_vision_dictionary = [{
            'mask': mask['segmentation'],
            'area': mask['area'],
            'bbox': mask['bbox'],
            'combined_area': 0,
            'class': None, # self._food_classification(mask['segmentation']),
            'attached_to': -1,
        } for mask in sorted(self.sam_result, key=lambda x: x['area'], reverse=True)]

    def _init_mask_dictionary(self):
        self.height, self.width = self.diet_vision_dictionary[0]['mask'].shape
        self.mask_dictionary = np.full((self.height, self.width), -1)

        for mi, item in enumerate(self.diet_vision_dictionary):
            x, y, w, h = item['bbox']
            item.update({'attached_to': mi})
            
            for row in range(y, y+h+1):
                for col in range(x, x+w+1):
                    if item['mask'][row][col]:
                        if self.mask_dictionary[row][col] == -1:
                            self.mask_dictionary[row][col] = mi

    def _generate_blank_transparent_image(self):
        transparent_image_file_name = 'blank_transparent_image.png'
        self.blank_transparent_image_path = os.path.join(self.HOME, 'images', transparent_image_file_name)

        if not os.path.exists(self.blank_transparent_image_path):
            blank_white_image = 255 * np.ones((self.height, self.width, 3), dtype = np.uint8)
            im_rgba = Image.fromarray(blank_white_image).convert('RGBA')
            im_rgba_data = im_rgba.getdata()
            im_rgba_new_data = []

            for item in im_rgba_data:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    im_rgba_new_data.append((255, 255, 255, 0))
                else:
                    im_rgba_new_data.append(item)

            im_rgba.putdata(im_rgba_new_data)
            im_rgba.save(self.blank_transparent_image_path, "PNG")

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

        self._cleanup_image_stack()
        self._overlay_image_stack.append(overlay_image_path)

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
    
    def _find_attached_index_list(self, selected_index: int) -> list:
        target_index = self.diet_vision_dictionary[selected_index]['attached_to']

        index_set = set([target_index])

        for mask_idx, segment_object in enumerate(self.diet_vision_dictionary):
            if segment_object['attached_to'] == target_index:
                index_set.add(mask_idx)

        return sorted(list(index_set))

    def find_mask_index_list(self, bbox_plot: list, is_collect: bool = False) -> list:
        x1, y1, x2, y2 = bbox_plot

        index_set = set()

        for row in range(y1, y2+1):
            for col in range(x1, x2+1):
                curr_mask_index = self.mask_dictionary[row][col]
                if curr_mask_index > -1:
                    index_set.add(curr_mask_index)

        if is_collect:
            lst = self._index_group_list.copy()
            self._index_group_list = sorted(list(set(lst) ^ index_set))

            return self._index_group_list

        return sorted(list(index_set))

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
    
    def _generate_imagearray_from_mask(self, mask_by_sam: np.ndarray) -> np.ndarray:
        """
        """
        original_image = cv2.imread(self.image_path)
        original_image = original_image.copy()
        mask = np.repeat(mask_by_sam[:, :, np.newaxis], 3, axis=2).copy() 
        filled_mask = np.where(mask, np.uint8(original_image), mask)

        return cv2.cvtColor(filled_mask, cv2.COLOR_BGR2RGB)
    
    def get_data_by_mask_index(self, mask_index: int) -> any:
        dict_data = self.diet_vision_dictionary[mask_index]
        mask_indices = self._find_attached_index_list(mask_index)
        mask_at_given_index = self._combine_masks(mask_indices)

        if dict_data['class'] == None:
            food_array = self._generate_imagearray_from_mask(mask_at_given_index)
            food_class = self._food_classification(food_array)
            
            for idx in mask_indices:
                self.diet_vision_dictionary[idx]['class'] = food_class

        return dict_data['class'], self._sum_area_of_selected_index_list(mask_indices)
    
    def _sum_area_of_selected_index_list(self, mask_index_list: list) -> int:
        """TODO make it pythonic
        """
        area = 0

        for idx in mask_index_list:
            area += self.diet_vision_dictionary[idx]['area']

        return area
    
    def correct_food_class(self, correct_food_class: str) -> None:
        parent_index = min(self._index_group_list)
        for idx in self._index_group_list:
            self.diet_vision_dictionary[idx].update({ 
                'class': correct_food_class, 
                'attached_to': parent_index 
            })

        if self._index_group_list:
            self._index_group_list.clear()

    def update_mask_index_list(self, lst: list) -> list:
        return sorted(list(set(lst) ^ set(self._index_group_list)))
    
    def expand_mask_index_list(self, index_list: list) -> list:
        lst = index_list.copy()

        for idx in index_list:
            lst += self._find_attached_index_list(idx)

        return sorted(list(set(lst)))