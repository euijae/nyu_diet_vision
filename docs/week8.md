# Week 8 (July 9 - 15, 2023)

## Last week

- (ideally) highlight segment object
- selection option must be flexibility and easy (like shift + select)
- and then use can correct our prediction

## Study

### Improve Object Annotator and Design of the DietVision app

The report can be found [here](./report/week8_report.md)

### Feature of DietVision app 

1. [x] 1) Clip to identify the food in the 101 categories
1. [x] 2) SAM to segment and get the area of the different segments.
1. [x] 3) SAM to isolate the segments.
1. [x] 4) Volume estimation of the whole meal using HelloPhotogrammetry, yielding volume
1. [x] 5) Allocate to each segment the proportion of the volume based on that segment's area with respect to the area of all the food (Example: If fish occupies 30% of the food area then allocate 30% of volume to the fish).
1. [x] 6) Use SAM to get the volume of each component
1. [ ] 7) Use SAM to segment -> User clicks on parts that are actually food.
1. [ ] 8) User indicates which is food and corrects any guesses that SAM has made. Merge masks.
1. [ ] 9) UI (Drag to get a bounding box, upload an image) + Run it on the cloud server or local (cloud server = heroku, local = gradio)**

**Outcome**: Given the volume of each item, need to map that into grams and then into nutritional value for our four nutrients (nutrients for each segment total nutrients for all segments).

### Plan for the rest of the semester

Based on the pending items listed above, here's a plan for the rest of the semester

1. Week 9 (7/16 - 22): Item 7 + 8. They are related to each other. Expect to get it done within a span of 2 weeks.
2. Week 10 (7/23 - 29): Item 7 + 8. 
3. Week 11 (7/30 - 8/5): Item 9. Can't underestimate this item. Sometimes, we run into a lot of unexpected issues when we make our implementations runnable and deployable. So, I expect to get it done within a span of 2 weeks. 
4. Week 12 (8/6 - 8/12): Item 9.

## Next week
