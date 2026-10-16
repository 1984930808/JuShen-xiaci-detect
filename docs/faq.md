# 常见问题解答 (FAQ)

## 安装问题

### Q1: pyzbar 安装失败怎么办？

**Windows**:
```bash
# 需要安装 Visual C++ 运行库
# 下载链接: https://aka.ms/vs/17/release/vc_redist.x64.exe
# 安装后重新运行: pip install pyzbar
```

**Linux**:
```bash
sudo apt-get install libzbar0
pip install pyzbar
```

**macOS**:
```bash
brew install zbar
pip install pyzbar
```

### Q2: 中文路径无法读取图像？

系统已内置 `imread_unicode()` 函数支持中文路径。

**解决方案**：
1. 确保使用 Python 3.8+
2. 检查文件名不包含特殊字符
3. 使用项目提供的读图函数，不要直接调用 `cv2.imread()`

```python
# ✅ 正确做法
from QRDecode import imread_unicode
img = imread_unicode("中文路径/图像.jpg")

# ❌ 错误做法
import cv2
img = cv2.imread("中文路径/图像.jpg")  # 会返回None
```

### Q3: CUDA 不可用怎么办？

检查步骤：
```bash
# 1. 检查CUDA是否安装
python -c "import torch; print(torch.cuda.is_available())"

# 2. 如果返回False，检查NVIDIA驱动
nvidia-smi

# 3. 重新安装CUDA版本的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**注意**：CPU模式也能运行，只是速度较慢（约2-5倍）。

## 运行问题

### Q4: 模型文件缺失提示？

```
[WARNING] 未找到模型文件: models\best.pt，使用配置模式
```

这是**正常提示**，不影响使用。系统有两种运行模式：

**配置模式**（无模型文件）：
- 基于LabelImg标注文件模拟检测
- 适合功能演示和流程验证

**模型模式**（有模型文件）：
- 真实的YOLO推理
- 需要训练或下载预训练权重

### Q5: QR码识别失败？

**可能原因**：
1. 图像模糊或光照不足
2. QR码损坏或打印质量问题
3. 图像分辨率过低

**解决方案**：
```python
# 检查图像质量
from QRDecode import decode_qr, imread_unicode
img = imread_unicode("path/to/image.jpg")

# 尝试图像增强
import cv2
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, enhanced = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

qr_data = decode_qr(enhanced)
```

### Q6: 检测速度慢？

**性能对比**：
| 环境 | 单样品耗时 | 优化建议 |
|------|-----------|----------|
| CPU (i5) | 0.8-1.5s | 使用GPU |
| CPU (i7) | 0.3-0.8s | 已是较好性能 |
| GPU (CUDA) | 0.05-0.15s | 最佳性能 |

**优化方法**：
1. 使用GPU加速
2. 调整 `config.yaml` 中的 `time_factor` 参数
3. 批量检测而非单个检测

## 数据和标注

### Q7: 如何添加自定义样品？

**步骤**：
1. 准备三视角图像：
   ```
   data/front/{id}-1.jpg  # 正面
   data/side/{id}-3.jpg   # 侧面
   data/back/{id}-2.jpg   # 背面
   ```

2. 更新MES数据库（`MES-ID.cgf`）：
   ```text
   {正面QR码},{期望条码},1
   ```

3. 刷新样品列表（菜单栏 → 文件 → 刷新样品列表）

### Q8: 如何标注瑕疵？

**推荐使用LabelImg**：

```bash
# 安装LabelImg
pip install labelimg

# 启动标注工具
labelimg data/front data/front/annotations
```

**标注要求**：
- 格式：PASCAL VOC (`.xml`)
- 保存位置：`data/front/annotations/{id}-1.xml`
- 类别：可根据实际瑕疵类型自定义

详细教程：[数据标注指南](dataset/labeling.md)

### Q9: MES数据库格式说明

**格式**：
```text
正面QR码,侧面背面条码,质检标记[,x:y,...]
```

**字段说明**：
| 字段 | 必需 | 说明 | 示例 |
|------|------|------|------|
| 正面QR | ✅ | 工件主ID | `PROD001` |
| 条码 | ✅ | 侧面/背面Code128 | `BC00123` |
| 质检标记 | ✅ | 1=良品, 0=不良 | `1` |
| x:y | ❌ | 瑕疵坐标点 | `320:180` |

**示例**：
```text
qjG8o3TPd1Z,9C0EA9EC,1
OqfSJH6wKG5,842ccafd,0,320:180,450:200
```

## 故障排查

### Q10: 检测异常如何调试？

**查看日志**：
```bash
# 日志位置
logs/inspection_YYYYMMDD.log

# 查看最新日志
tail -f logs/inspection_*.log
```

**详细错误信息**：
```python
# 在pipeline.py中添加调试输出
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Q11: 界面卡顿或无响应？

**原因**：检测在主线程运行，阻塞UI

**解决方案**：
- 项目已实现多线程异步检测
- 如仍有问题，检查CPU占用率
- 关闭其他占用资源的程序

### Q12: 如何批量检测？

**编写批处理脚本**：
```python
from pathlib import Path
from pipeline import InspectionPipeline

pipeline = InspectionPipeline("MES-ID.cgf", "models/best.pt")
DATA_ROOT = Path("data")

# 批量检测样品1-10
results = []
for i in range(1, 11):
    result = pipeline.inspect_sample_dir(DATA_ROOT, str(i))
    results.append({
        "sample_id": i,
        "overall": result.overall,
        "message": result.overall_message
    })
    
# 导出结果
import pandas as pd
df = pd.DataFrame(results)
df.to_csv("batch_results.csv", index=False)
```

## 其他问题

### Q13: 支持哪些操作系统？

**已测试**：
- ✅ Windows 10/11
- ✅ Ubuntu 20.04/22.04
- ✅ macOS 11+

**要求**：
- Python 3.8 - 3.11
- 推荐 Python 3.10

### Q14: 可以用于生产环境吗？

**可以，但需要**：
1. 使用真实的YOLO模型（非配置模式）
2. 配置GPU加速
3. 优化检测参数
4. 集成到现有MES系统
5. 进行充分的现场测试

**部署指南**：参考 [DEPLOYMENT.md](../DEPLOYMENT.md)

### Q15: 如何获取技术支持？

**渠道**：
- 📚 查看 [完整文档](README.md)
- 🐛 [提交Issue](https://github.com/1984930808/JuShen-xiaci-detect/issues)
- 💬 [参与讨论](https://github.com/1984930808/JuShen-xiaci-detect/discussions)

**提交Issue时请提供**：
- 操作系统和Python版本
- 完整的错误信息
- 复现步骤
- 相关日志文件
