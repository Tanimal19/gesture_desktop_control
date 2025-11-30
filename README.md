
DISPLAY_WIDTH = 1512  
DISPLAY_HEIGHT = 982  
CAMERA_WIDTH = 1620  
CAMERA_HEIGHT = 1080  


## Data Collection & Model Training

Generate task configuration files
```bash
python -m data_collection.task_generator
```

Run data collection app for each participant 
```bash
python -m data_collection.app
```

Post-process collected data and manual labeling:  
merge all participant data, initialize labeled csv files
```bash
python -m data_collection.postprocess
```

Manually labeling for participant 0
```bash
python -m data_collection.manual_labeling
```

Training annotator model for each task using manually labeled data
```bash
python -m gesture_model.task_annotator.train
```

Auto-labeling for all participants using trained annotator models
```bash
python -m data_collection.auto_labeling
```

Train gesture recognition model using the fully labeled dataset
```bash
python -m gesture_model.gtcn.train
```

Post analysis for labeled dataset and trained models
```bash
python -m data_collection.post_analysis
```


## Evaluation Study
