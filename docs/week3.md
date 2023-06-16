# Week 3 (June 4 - June 10, 2023)

## Last week

- [Volume Estimation] Image - Minimum required angle (360 is unreal)
- [Volume Estimation] Light brightness affects the outcome?
- [Volume Estimation] Food is not isolated, can we still compute it?
- [Segmentation] Gray out if it's not a food.
- Note: Never try to be perfectionist

## Study

### [Volume Estimation] Minimum Required Angle

This is to verify if the complete angle of the object is required. In conclusion, every possible angle of the image improves the accuracy of the object generation. 

### [Volume Estimation] Adjust Brightness 

This is to verify if the brightness makes an impact on the outcome 3D object. HelloPhotogrammetry doesn't adjust the brightness and it generates the 3D object as it's shown in the image. 

### [Volume Estimation] 3D food segmentation

This is to verify if HelloPhotogrammetry is capable of generating a 3D object for each food in the image. The tool doesn't generate the object for each food in the image. It counts a group of foods as a single object.

### [Segmentation] Food specific segmentation

Meta's SAM stands for Segment Anything Model. I am still trying to figure out how to segment a specific group of object.

## Next week

- 360 is fine
- segmentation => annotation the food only (opting out the gray out option)
