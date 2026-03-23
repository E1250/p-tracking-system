from enum import Enum

#TODO put this in config file.
class YOLOExportFormats(Enum):
    torch = "torch"                 # Default
    onnx = "onnx"                     
    coreml = "coreml"                 # OpenML for Apple
    torchscript = "torchscript"       # Optimized PyTorch for C++ envs
    engine = "engine"                 # TensorRT
    tflite = "tflite"                 # Mobile and Embedded devices

DEPTH_MODEL_CONFIG = {
    'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
    'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
    'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]},
    'vitg': {'encoder': 'vitg', 'features': 384, 'out_channels': [1536, 1536, 1536, 1536]}
}