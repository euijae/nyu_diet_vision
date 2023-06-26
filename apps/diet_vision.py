from food_classification import classify_food

def diet_vision(image):
    segmented_images = segment_image(image)
    food_contents = {}
    total_area = 0
    
    for segmented_image in segmented_images:
        if is_food(segmented_image):
            food_class, area = classify_food(segmented_image)
            total_area = total_area + area
            food_contents.update({ food_class, area, segmented_image })
    
    for food in food_contents:
        compute_nutritions_and_volume(food)
        
def segment_image(image):
    pass

def is_food(segmented_image):
    pass

def compute_nutritions_and_volume(food):
    pass