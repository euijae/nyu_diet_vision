# Report of the Week: July 9 - 15, 2023

## Recap

- Each segment needs to be selectable and annotator should put a border around a selected object (not put it in a box).
- Segment selection should be smooth (e.g, dragging multiple segments at once).

## Study

### Design of DietVision

#### Data

SAM must be running to get a set of masks at start of DietVision app. Once SAM calculates masks and their area, we should store these core data into a Python dictionary and the schema looks as below. This must be a global variable and should be loaded anywhere within an applicatin and destroyed once the app session is ended or user clears an uploaded image.

```python
DIET_VISION_DICTIONARY: dictionary = {
  [index: int]: {
    mask: numpy.ndarray,  # m x n matrix, same size as the image
    area: int,            # a number of pixels are in the region of the mask
    class: string         # None if it's not a food, otherwise CLIP or user can classify
  }
}
```

**DEMO** Another global variable for the app. Each entry represents an index of mask that a pixel belongs to. For example, the coordinate (x, y) = (1800, 1000) belongs to the fried chip. The mask at index 2 is a mask of the fried chip. So,  `MASK_DICTIONARY[x, y] = 2`. 

```python
MASK_DICTIONARY: numpy.ndarray
[[(0,0), (0,1), ... , (0, w-1)]]       # w = width
[[(1,0), (1,1), ... , (1, w-1)]]
....
[[(h-1,0), (h-1,1), ... , (h-1, w-1)]] # h = height
```

**DEMO** First draft of DietVision UI

**DEMO** Group segments. Masks are not placed in a line. Mouse drag on an image yields a bounding box. For example, dragging spots four coordinates e.g, (0, 0), (0, 10), (10, 0), and (10, 10) and mask indices belong to the bounding box are 20 and 82, we can pick corresponding masks from `DIET_VISION_DICTIONARY` and combine them.

## Next Week

Item 7 and 8 ([link](https://github.com/euijae/nyu_diet_vision/blob/week8/docs/week8.md#feature-of-dietvision-app))

- 1. Segmentation and then user assigns foods to segments using Thibault’s database
- 2. Volume estimation
- 3. See how well we do on meals where we know the nutritional content
