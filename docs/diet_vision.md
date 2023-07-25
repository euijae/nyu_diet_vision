# DietVision

## Behind the Scene

1. Segment objects in image
2. Classifiy objects
3. Then calculate food's nutritional data

## Image Segmentation

### Segment Anything Model

Meta AI has released the Segment Anything Model (SAM), a new open source AI model that can segment any object in an image or video with a single click.
The image 

Original image             |  Segmented image
:-------------------------:|:-------------------------:
![](../../apps/images/fish_chips.jpg)  |  ![](../images/annotated_image.png)

### Mask

A mask is a binary image consisting of zero and non-zero values.
Typically, each pixel is assigned a number between 0 and 255, where 0 represents the complete absence of light (black) and 255 represents complete saturation of light (white).

The image on the left is the mask of the table. The other image shows table without masking and applying grayscale color.

Masked table             |  Unmasked table (gray)
:-------------------------:|:-------------------------:
![](../images/classification_mask_fried_fish.jpg)  |  ![](../images/classification_unmask_fried_fish.jpg)

## Image Classification

## Demo

