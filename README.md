
DISPLAY_WIDTH = 1512  
DISPLAY_HEIGHT = 982  
CAMERA_WIDTH = 1620  
CAMERA_HEIGHT = 1080  





- `data_collection/task_generator.py`: Script to generate data collection tasks
- `data_collection/app.py`: Main application for data collection


- `gesture_model/model.py`: Gesture recognition model definition
- `gesture_model/datasets/.npy`: Training data



|               | thumb_index_dist | thumb_middle_dist | index_middle_dist |
| ------------- | ---------------- | ----------------- | ----------------- |
| left_press    | decreasing       | stable            | increasing        |
| left_release  | increasing       | stable            | decreasing        |
| right_press   | stable           | decreasing        | increasing        |
| right_release | stable           | increasing        | decreasing        |
| scroll_up     | increasing       | increasing        | stable            |
| scroll_down   | decreasing       | decreasing        | stable            |