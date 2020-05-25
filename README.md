# Aerial-Imagery-and-OpenStreetMap-Retrieval

To replicate our result, please first create a conda environment with the following packages installed:

- python 3.7.7
- opencv 3.4.2
- Overly 0.2
- matplotlib 3.1.3
- Requests 2.23.0
- numpy 1.18.4

Before running the program, change ```map_area``` on line 193 to your desired coordinate. The coordinate follows the format [latitude1, longitude1, latitude2, longitude2]. The default coordinate is the Campus of Northwestern University. 

To get the overlay of Bing Map image on OpenStreeMap road network image, run:

```
python aerial_road_img.py path_to_output_dir/
```


