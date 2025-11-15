
DISPLAY_WIDTH = 1512  
DISPLAY_HEIGHT = 982  
CAMERA_WIDTH = 1620  
CAMERA_HEIGHT = 1080  

## Mediapipe Landmarks
- `screen_landmarks` (x, y, z): Normalized coordinates of hand landmarks on the image in pixel.
  - the origin (0,0) is at the top-left corner of the image.
  - x and y are normalized to [0.0, 1.0] by the image width and height respectively.
  - z represents the landmark depth with the smaller value representing closer to the camera. The magnitude of z uses roughly the same scale as x.
- `world_landmarks` (x, y, z): Real world 3D coordinates of hand landmarks in meters.
  - The origin is at the center of the hand.
  - The x-axis extends to the right of the hand, the y-axis extends upward from the hand, and the z-axis extends outward from the back of the hand.