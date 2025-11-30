import torch
import numpy as np
from gesture_model import AbstractGestureModel, GestureLabel
from share.utils import HandLandmark


class GestureModelRunner:
    def __init__(self, model: AbstractGestureModel, model_path: str, device: str):
        self.device = device
        self.model = model
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def inference(self, landmark_window: np.ndarray) -> GestureLabel:
        """
        landmarks_window: np.array of shape (WINDOW_LENGTH, len(HandLandmark), 3)\n
        """
        assert (
            landmark_window.shape[1] == len(HandLandmark)
            and landmark_window.shape[2] == 3
        )

        with torch.no_grad():
            x_tensor = self.model.landmarks_window_to_X(landmark_window)
            x_tensor = x_tensor.unsqueeze(0)  # add batch dimension
            x_tensor = x_tensor.to(next(self.model.parameters()).device)
            out = self.model.forward(x_tensor)
            pred_idx = out.argmax(dim=1).item()
            mappped_label = self.model.y_to_label(pred_idx)

        return mappped_label
