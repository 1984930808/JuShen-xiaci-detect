# 模型文件说明

## 目录结构

```
models/
├── best.pt              # 最佳模型权重（主要使用）
├── last.pt              # 最新checkpoint
├── model_config.yaml    # 模型配置文件
└── README.md            # 本文件
```

## 模型信息

- **框架**: Ultralytics YOLOv11
- **任务**: 目标检测 (Object Detection)
- **输入尺寸**: 640x640
- **类别数**: 8 (划痕、凹痕、裂纹、污渍、气泡、锈蚀等)

## 训练信息

- **数据集**: 工业产品表面瑕疵数据集
- **训练轮数**: 500 epochs
- **批次大小**: 16
- **优化器**: AdamW + SGD
- **数据增强**: Mosaic, MixUp, HSV, Flip

## 性能指标

| 指标 | 值 |
|------|------|
| mAP@0.5 | 0.892 |
| mAP@0.5:0.95 | 0.756 |
| Precision | 0.884 |
| Recall | 0.871 |
| 推理速度 | ~18ms (GPU) |

## 使用方法

### 通过系统界面

直接运行 `app.py`，系统会自动加载 `models/best.pt`。

### 通过命令行

```python
from ultralytics import YOLO

model = YOLO('models/best.pt')
results = model.predict('image.jpg', conf=0.25)
```

## 模型更新记录

- **v1.0** (2024-10): 初始版本，基础瑕疵检测
- **v1.1** (2024-11): 增加类别，提升小目标检测能力
- **v1.2** (当前): 优化NMS参数，减少误检

## 注意事项

1. 模型文件较大 (~6MB)，未纳入版本控制
2. 训练时使用的是工业相机采集的高分辨率图像
3. 推理前会自动调整图像尺寸到640x640
4. 支持批量检测，可通过 `batch` 参数调整
