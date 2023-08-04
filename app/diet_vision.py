import calendar
import cv2
import datetime
import random
import torch
import os

import supervision as sv
import numpy as np
import itertools as it

from pathlib import Path
from PIL import Image
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator


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

    def upload_image(self, image_name):
        self.image_directory = os.path.join(self.HOME, 'images')
        
        self.image_path = os.path.join(self.image_directory, image_name)
        self.image_brg = cv2.imread(self.image_path) # np.ndarray
        self.original_image = cv2.cvtColor(self.image_brg, cv2.COLOR_BGR2RGB) # np.ndarray
        
        # app_posix = Path(__file__).parent.parent.absolute() / "app"
        # app_home = str(app_posix.as_posix())
        # with open(f'{app_home}/sam_result.npy', 'rb') as f:
        #     self.sam_result = np.load(f, allow_pickle=True).copy()

        self.sam_result = self.mask_generator.generate(self.original_image)

        self._init_diet_vision_dictionary()
        self._generate_blank_transparent_image()

        return self.create_overlay_image()

    def _init_diet_vision_dictionary(self):
        """One time set up at image upload"""
        self.raw_diet_vision_dictionary = [{
            'mask': mask['segmentation'],
            'area': mask['area'],
            'class': None,
            'attached_to': idx,
            'nonzero_at': set(np.rec.fromarrays(np.nonzero(mask['segmentation'])).tolist())
        } for idx, mask in enumerate(sorted(self.sam_result, key=lambda x: x['area'], reverse=True))]
        
        self.height, self.width = self.raw_diet_vision_dictionary[0]['mask'].shape

        mask_dictionary = np.full((self.height, self.width), -1)

        for idx, curr_dvd in enumerate(self.raw_diet_vision_dictionary):
            for pixel in curr_dvd['nonzero_at']:
                if mask_dictionary[pixel] == -1:
                    mask_dictionary[pixel] = idx
                else:
                    mask_dictionary[pixel] = min(idx, mask_dictionary[pixel])

                curr_dvd['attached_to'] = mask_dictionary[pixel]

        dict_mask_groups = {}

        for idx, dvd in enumerate(self.raw_diet_vision_dictionary):
            if dvd['attached_to'] in dict_mask_groups:
                dict_mask_groups[dvd['attached_to']].append(idx)
            else:
                dict_mask_groups.update({dvd['attached_to']: [idx]})

        self.diet_vision_dictionary = [{
            'mask': self._combine_masks_init(v),
            'class': None,
            'attached_to': idx,
            'nonzero_at': set(np.rec.fromarrays(np.nonzero(self._combine_masks_init(v))).tolist()),
            'area': len(set(np.rec.fromarrays(np.nonzero(self._combine_masks_init(v))).tolist()))
        } for idx, v in enumerate(dict_mask_groups.values())]

    def _generate_blank_transparent_image(self):
        """One time set up at image upload"""
        transparent_image_file_name = 'blank_transparent_image.png'
        self.blank_transparent_image_path = os.path.join(self.HOME, 'images', transparent_image_file_name)

        if os.path.exists(self.blank_transparent_image_path):
            os.system(f'rm {self.blank_transparent_image_path}')

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

    def create_overlay_image(self, is_all: bool = True, indices: list = None) -> str:
        """Annotate mask and put that on blank image"""
        transparent_image_test = cv2.imread(self.blank_transparent_image_path)
        transparent_image_test = transparent_image_test.copy()
        annotated_mask_test = self._generate_image_annotator() if is_all else self._spot_annotator_on_mask(indices)

        img1_test = Image.fromarray(transparent_image_test).convert('RGBA')
        img2_test = Image.fromarray(annotated_mask_test).convert('RGBA')

        img_test_new_data = []

        for item in img2_test.getdata():
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                img_test_new_data.append((255, 255, 255, 0))
            else:
                a, b, c, _ = item
                img_test_new_data.append((a, b, c, 195))

        date = datetime.datetime.utcnow()
        utc_time = str(calendar.timegm(date.utctimetuple()))

        image_name = f'annotator_image_{utc_time}.png' if is_all else f'overlay_image_{utc_time}.png'
        overlay_image_path = os.path.join(self.HOME, 'images', image_name)
        
        img1_test.putdata(img_test_new_data)        
        img1_test.save(overlay_image_path, "PNG")

        # self._cleanup_image_stack()
        # self._overlay_image_stack.append(overlay_image_path)

        return overlay_image_path

    def _generate_image_annotator(self) -> np.ndarray:
        size = len(self.diet_vision_dictionary)
        lst = list(range(0, size))
        mask_index_set = set(lst)
        overlay_image = None

        for idx in lst:
            if idx in mask_index_set:
                mask_index_list = self._find_attached_index_list(idx)
                print(f'{idx} = {mask_index_list}')
                # mask_index_set -= set(mask_index_list)

                if overlay_image is None:
                    overlay_image = self._spot_annotator_on_mask(mask_index_list)

                overlay_image += self._spot_annotator_on_mask(mask_index_list)

        return overlay_image

    def _spot_annotator_on_mask(self, indices: list) -> np.ndarray:
        """(utlity) Annotate mask and put that on blank image"""
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
    
    def _combine_masks(self, index_list: list) -> np.ndarray:
        """(utlity) Annotate mask and put that on blank image"""
        i0 = index_list[0]
        combined_mask = self.diet_vision_dictionary[i0]['mask'].copy()

        for idx in index_list[1:]:
            curr_mask = self.diet_vision_dictionary[idx]['mask'].copy()
            combined_mask = np.logical_or(combined_mask, curr_mask)

        return combined_mask
    
    def _combine_masks_init(self, index_list: list) -> np.ndarray:
        """(utlity) Annotate mask and put that on blank image"""
        i0 = index_list[0]
        combined_mask = self.raw_diet_vision_dictionary[i0]['mask'].copy()

        for idx in index_list[1:]:
            curr_mask = self.raw_diet_vision_dictionary[idx]['mask'].copy()
            combined_mask = np.logical_or(combined_mask, curr_mask)

        return combined_mask

    def find_mask_index_list(self, bbox_plot: list, is_collect: bool = False) -> list:
        x1, y1, x2, y2 = bbox_plot

        index_set = set()
        diet_vision_dictionary_size = len(self.diet_vision_dictionary)

        for row, col in it.zip_longest(range(y1, y2+1), range(x1, x2+1)):
            for idx in range(0, diet_vision_dictionary_size):
                if (row, col) in self.diet_vision_dictionary[idx]['nonzero_at']:
                    index_set.add(idx)

        if is_collect:
            lst = self._index_group_list.copy()
            self._index_group_list = sorted(list(set(lst) ^ index_set))

            return self._index_group_list

        return sorted(list(index_set))
    
    def get_data_by_mask_index(self, mask_index: int) -> any:
        """retrieve food class and its area"""
        dict_data = self.diet_vision_dictionary[mask_index]
        mask_indices = self._find_attached_index_list(mask_index)

        food_class = dict_data['class'] if dict_data['class'] else 'undetermined'
        return food_class, self._sum_area_of_selected_index_list(mask_indices)
    
    def _find_attached_index_list(self, selected_index: int) -> list:
        """(utility) retrieve food class and its area"""
        target_index = self.diet_vision_dictionary[selected_index]['attached_to']

        index_set = set()

        for mask_idx, segment_object in enumerate(self.diet_vision_dictionary):
            if segment_object['attached_to'] == target_index:
                index_set.add(mask_idx)

        return sorted(list(index_set))

    def _sum_area_of_selected_index_list(self, mask_index_list: list) -> int:
        """(utility) retrieve food class and its area"""
        area = 0

        for idx in mask_index_list:
            area += self.diet_vision_dictionary[idx]['area']

        return area
    
    def update_food_class(self, updated_food_class: str) -> None:
        if self._index_group_list:
            parent_index = min(self._index_group_list)
            for idx in self._index_group_list:
                self.diet_vision_dictionary[idx].update({ 
                    'class': updated_food_class, 
                    'attached_to': parent_index 
                })

            self._index_group_list.clear()
