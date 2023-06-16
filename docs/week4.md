# Week 4 (June 11 - June 17, 2023)

## Last week

- [volume estimation] 360 is fine
- [segmentation] classify the food only. Gray out if an object is not a food.

## Study

The report can be found [here](./report/food_only_annotation.MD)

## Next week

- Clip to map to the 101 food directly without SAM
- Use sam to segment and get the area of the different segments.
- User indicates which is food and corrects any guesses that SAM has made.
- volume estimation of the whole meal using hellophotogramatry.
- allocate to each segment the proportion of the volume based on that segment's area wwith rspect to the area of all the food. If fish occupies 30% of the food area then allocate 30% of the volume oto the fish.
- Use SAM to get the volume of each component
- Use SAM to segment -> User clicks on parts that are actually food.
- SAM to isolate the segments.
