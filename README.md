
DISPLAY_WIDTH = 1512  
DISPLAY_HEIGHT = 982  
CAMERA_WIDTH = 1620  
CAMERA_HEIGHT = 1080  


## Data Collection & Model Training

1. Generate task configuration files
    ```
    python data_collection/task_generator.py
    ```

2. Run data collection app for each participant
    ```
    python data_collection/app.py
    ```

3. Post-process collected data and manual labeling
    ```
    python data_collection/postprocess.py
    ```
    - merge all participant data
    - initialize labeled csv files

4. Manually labeling for participant 1
    ```
    python data_collection/manual_labeling.py
    ```

5. Training annotator model for each task using manually labeled data
    ```
    python gesture_model/train_annotator.py
    ```

6. Auto-labeling for all participants using trained annotator models
    ```
    python data_collection/auto_labeling.py
    ```

7. Train gesture recognition model using the fully labeled dataset
    ```
    python gesture_model/train_gesture_model.py
    ```

## Evaluation Study
