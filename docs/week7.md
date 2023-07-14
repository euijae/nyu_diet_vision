# Week 7 (July 2 - 8, 2023)

## Last week

- Each segmented object should be clickable
  - let user get involved.
  - user can also select/group segmented objects (just like google image 'select' option).
  - opting out "gray out" annotation!

## Study

### Clickable Segment

Meta's SAM segments objects detected in the given image and a number of metadata is provided. One of them is the bounding box which is a type of integer array with four elements in XYWH format. I used this data to plot a box border around each segmentation. Once a box border is set, I used JavaScript to place an anchor tag on top of each bounding box. 

A link to demo: https://share.vidyard.com/watch/PNck93f1FLmpNUHa1Fn5Jd?

## Next week

- (ideally) highlight segment object
- selection option must be flexibility and easy (like shift + select)
- and then use can correct our prediction
