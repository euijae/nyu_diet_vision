# Report of the Week: June 18 - 24, 2023

## Recap

We came up with the future plan last week. This week, the main goal was to implement the function to achieve the following:

1. SAM segments objects in the given image
1. Iterate each segmented object to determine if the object is food or not using CLIP
1. Calculate the area of the classified food
1. Compute the nutrition of each food and its volume

Below is a pseudocode of the steps above.

```python
 1 def diet_vision(image):
 2    segmented_images = sam_segmentation(image)
 3    food_contents = {}
 4    total_area = 0
 5    
 6    for segmented_image in segmented_images:
 7        if is_food(segmented_image):
 8            food_class, area = clip_classify_food(segmented_image)
 9            total_area = total_area + area
10            food_contents.update({ food_class, area, segmented_image })
11
12    for food in food_contents:
13        compute_nutritions_and_volume(food)
```

## Food Classification

### Logic to classify an object into 101 food classes 

Note: Entire 101 classes can be found [here](./food101_list.txt)

CLIP is trained with the Food 101 model. 
CLIP processes the input image and returns an array with 101 elements. 
Each element indicates the probability that a corresponding food class is observed. 
For example, in the array below, the maximum value is `6.268926` and it's at the index `81` (zero based) and the corresponding food class is `ramen`.

```shell script
[[1.644355   1.9569811  1.9791466  2.7934716  1.2358488  1.0498573
  1.4632063  3.1302524  2.6898437  2.7769027  1.0088788  3.9173887
  1.7461522  1.7126582  1.7405503  4.0664873  1.7554799  3.1865432
  5.0988293  3.176433   3.2288623  1.4228518  1.5513251  0.6511564
  4.484393   3.411488   2.8123903  1.8566742  2.3002577  2.2710168
  1.9095688  1.3543427  3.9719748  2.3179684  2.262222   2.5328355
  1.678452   2.3729846  2.8626099  3.3886726  1.6605937  3.6097538
  1.1243571  2.9541006  3.1849942  2.3735566  2.746877   2.1900578
  1.5853169  1.6037421  2.5980403  1.8457454  4.3209085  0.93616384
  5.3628154  1.1842313  2.55581    2.4484086  2.3995724  2.0944
  3.520659   2.579413   2.7242517  0.74008906 6.085831   2.4760447
  3.0944333  3.4360476  1.7819281  3.2981687  4.9098415  2.5720854
  1.8724896  2.629983   3.0622427  5.544302   1.6147127  3.2371635
  2.8070192  2.469132   2.2729614  6.268926   2.6342778  0.83783543
  2.897822   2.2280598  4.4151707  2.3624592  2.490876   3.3581512
  2.0417285  3.1966834  3.4929028  2.4374256  0.81385285 3.5190523
  2.5918264  4.8435206  1.7937648  1.4444551  0.9410287 ]]
```

The below table depicts a mapping between class and value when an input image is a ramen.

| #   | Class          | P-Value |
|-----|----------------|---------|
| 1   | apple_pie      | 1.644355|
| 2   | baby_back_ribs | 1.9569811|
|     | ...            |   ...   |
| 82  | ramen          | 6.268926|
|     | ...            |   ...   |
| 101 | waffles        | 0.9410287 |

### Ongoing Investigation

There's not a `not_food` option. It maps to any of the 101 classes regardless. 
What CLIP actually does is that it matches an object to one of 101 classes that is the most similar.

- [Not food image](../../apps/images/not_food.png) is classified as "fried_rice" with 3.028958
- [Not food image 2](../../apps/images/not_food2.png) is classified as "peking_duck" with 4.1906633
- [Ramen](../../apps/images/ramen.JPG) is classified as "ramen" with 6.268926
- [Stake](../../apps/images/stake.JPG) is classified as "ceviche" with 3.674295

Thus, the `is_food` function returns true for every `segmented_image`. 

```python
7  if is_food(segmented_image):
```

I'm working on what would be the reasonable cut-off P-value to determine if it's food or not.