import torch
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark
from gesture_model.utils import GestureLabel, GestureModel


class GestureModelRunner:
    def __init__(self, model: GestureModel, model_path: str, device: str):

        self.device = device
        self.model = model
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def run_inference(self, landmarks_window: np.ndarray) -> GestureLabel:
        assert (
            landmarks_window.shape[1] == len(HandLandmark)
            and landmarks_window.shape[2] == 3
        )
        return self.model.inference(landmarks_window)
