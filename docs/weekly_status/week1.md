# Week 1 (May 21 - 27, 2023)

## Meeting outcome from the previous week

Find the distance 

## Highlight

1. We noticed that the `HelloPhotoGrammetry` is not distance-agnostic.
2. A position where a photo was taken does matter.
3. As you further away, the 3D graphic (By `HelloPhotoGrammetry`) appears to be smaller.
4. As you approach, the 3D graphic becomes larger.
5. Segmentation becomes less accurate (or unavailable) as you further away.

## Experiments

|           |        Actual (W x D x H)        |                4 inches               |                7 inches               |               10 inches               |
|:---------:|:--------------------------------:|:-------------------------------------:|:-------------------------------------:|:-------------------------------------:|
|   Apple   |    300.3 <br> = 7 x 7.8 x 5.5    |   0.1941758 <br> =.65 x .658 x .454   | 0.043354828 <br> = .374 x .389 x .298 | 0.017019608 <br> = .281 x .268 x .226 |
| Chocolate |     9 <br>  = 4.5 x 2.5 x 0.8    |   0.0068595 <br> = .34 x .269 x .075  |         Too far. Can't detect         |         Too far. Can't detect         |
|    Coke   | 528.125 <br>  = 6.5 x 6.5 x 12.5 |  0.53392812 <br> = .671 x .698 x 1.14 |   0.07476804 <br>= .342 x .34 x .643  |  0.05710068 <br>= .315 x .312 x .581  |
|  Sandwich |      396 <br> = 12 x 5.5 x 6     | 0.151459374 <br>= .807 x .418 x . 449 | 0.092934156 <br> = .651 x .356 x .401 |  0.04102989 <br>= .445 x .254 x .363  |

## Correlations

- Coke shows consistent number changes. Drop to one tenth every 5-6 inches.
- Rectangular object results in a very close outcome. 
