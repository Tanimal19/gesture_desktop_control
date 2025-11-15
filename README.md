
DISPLAY_WIDTH = 1512  
DISPLAY_HEIGHT = 982  
CAMERA_WIDTH = 1620  
CAMERA_HEIGHT = 1080  


## change model parameters in gesture_model/model

## Training
generate training samples
```
python -m data_collection.annotation.training_data_build
```

train model
```
python -m gesture_model.train
```


