# from ai.depth.depth_anything_v2.depth_anything_v2.dpt import DepthAnythingV2
from depth_anything_v2.dpt import DepthAnythingV2

import torch
from pathlib import Path
import cv2 as cv
from typing import Literal
import numpy
from ai.utils.constants import DEPTH_MODEL_CONFIG

class DepthAnything:
    def __init__(self, 
        encoder: Literal["vits", "vitb", "vitl", "vitg"], 
        depth_model_path:Path | str, 
        DEVICE:Literal["cpu", "cuda", "mps"] = "cpu",
        f16 = False
        ):
        self.__model_config = DEPTH_MODEL_CONFIG
        self.model = DepthAnythingV2(**self.__model_config[encoder])
        self.model.load_state_dict(torch.load(depth_model_path, map_location=DEVICE))
        self.model = self.model.to(DEVICE).eval()
        self.DEVICE = DEVICE
        self.f16 = f16

    def depth(self, frame: numpy.ndarray | str) -> numpy.ndarray:
        """
        Getting the depth of the frame. 
        input: 
            frame as a file path not a numpy array. 
        return:
            depth as an image
        """
        if isinstance(frame, str):
            raw_img = cv.imread(frame)
        elif isinstance(frame, numpy.ndarray):
            raw_img = frame
        
        # infer_image preprocess the input to match the internal requirements, then output it again with the original shape..
        if (self.DEVICE == "cuda") and self.f16:
            with torch.autocast(device_type="cuda"):
                depth = self.model.infer_image(raw_img)
        else:
            depth = self.model.infer_image(raw_img)

        return depth

    def calculate_depth(self, frame:numpy.ndarray, points):
        """
        Calculate and return the depth of a specific box or point
        input: 
            frame as numpy array and not a path
        return:
            depth as a value of a grayscale image : Float
            array of (min, max) values of this gray scale. 
        """
        depth = self.depth(frame)
        
        depth_values = []
        for point in points:
            depth_values.append(((depth[point[1]][point[0]] - depth.min()) / (depth.max() - depth.min())).item())

        return depth_values