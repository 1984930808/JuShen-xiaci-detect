"""系统信息查看工具。"""

import platform
import sys
from pathlib import Path

try:
    import cv2
    CV2_VERSION = cv2.__version__
except:
    CV2_VERSION = "未安装"

try:
    import numpy as np
    NUMPY_VERSION = np.__version__
except:
    NUMPY_VERSION = "未安装"

try:
    from ultralytics import __version__ as YOLO_VERSION
except:
    YOLO_VERSION = "未安装"

try:
    import torch
    TORCH_VERSION = torch.__version__
    CUDA_AVAILABLE = torch.cuda.is_available()
    CUDA_VERSION = torch.version.cuda if CUDA_AVAILABLE else "N/A"
except:
    TORCH_VERSION = "未安装"
    CUDA_AVAILABLE = False
    CUDA_VERSION = "N/A"


def get_system_info() -> dict:
    """获取系统信息。"""
    return {
        "系统": platform.system(),
        "系统版本": platform.version(),
        "架构": platform.machine(),
        "处理器": platform.processor(),
        "Python版本": sys.version.split()[0],
        "Python路径": sys.executable,
        "OpenCV版本": CV2_VERSION,
        "NumPy版本": NUMPY_VERSION,
        "PyTorch版本": TORCH_VERSION,
        "YOLO版本": YOLO_VERSION,
        "CUDA可用": "是" if CUDA_AVAILABLE else "否",
        "CUDA版本": CUDA_VERSION,
    }


def print_system_info():
    """打印系统信息。"""
    print("=" * 60)
    print("系统信息")
    print("=" * 60)
    
    info = get_system_info()
    max_key_len = max(len(k) for k in info.keys())
    
    for key, value in info.items():
        print(f"{key:<{max_key_len + 2}} : {value}")
    
    print("=" * 60)


def check_requirements():
    """检查依赖是否满足。"""
    print("\n" + "=" * 60)
    print("依赖检查")
    print("=" * 60)
    
    requirements = {
        "OpenCV": CV2_VERSION != "未安装",
        "NumPy": NUMPY_VERSION != "未安装",
        "PyTorch": TORCH_VERSION != "未安装",
        "Ultralytics": YOLO_VERSION != "未安装",
    }
    
    all_ok = True
    for name, installed in requirements.items():
        status = "✓" if installed else "✗"
        print(f"{status} {name:<15} : {'已安装' if installed else '未安装'}")
        if not installed:
            all_ok = False
    
    print("=" * 60)
    
    if all_ok:
        print("✓ 所有依赖已满足")
    else:
        print("✗ 部分依赖缺失，请运行: pip install -r requirements.txt")
    
    print()
    
    return all_ok


if __name__ == "__main__":
    print_system_info()
    check_requirements()
