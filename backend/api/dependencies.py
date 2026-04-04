# Here exists function to use instead of using app.state directly in the main.py
from fastapi.requests import HTTPConnection

def get_detection_model(request: HTTPConnection):
    return request.app.state.detection_model

def get_depth_model(request: HTTPConnection):
    return request.app.state.depth_model

def get_safety_detection_model(request: HTTPConnection):
    return request.app.state.safety_detection_model

def get_redis(request: HTTPConnection):
    return request.app.state.redis