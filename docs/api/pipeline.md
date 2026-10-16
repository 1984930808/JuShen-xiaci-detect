# Pipeline API 文档

本文档详细介绍检测流水线的API接口。

## InspectionPipeline 类

主要的检测流水线类，负责协调三码比对和瑕疵检测。

### 初始化

```python
from pipeline import InspectionPipeline

pipeline = InspectionPipeline(
    mes_path="MES-ID.cgf",
    model_path="models/best.pt"
)
```

**参数**：
- `mes_path` (str | Path): MES配置文件路径
- `model_path` (str | Path | None): YOLO模型文件路径（可选）

### 核心方法

#### inspect_sample_dir

对指定样品目录执行完整检测。

```python
result = pipeline.inspect_sample_dir(
    data_root="data",
    sample_id="2"
)
```

**参数**：
- `data_root` (str | Path): 数据根目录
- `sample_id` (str): 样品编号

**返回**：`InspectionResult` 对象

**示例**：
```python
from pathlib import Path
from pipeline import InspectionPipeline

pipeline = InspectionPipeline("MES-ID.cgf", "models/best.pt")
result = pipeline.inspect_sample_dir(Path("data"), "2")

print(f"总体结论: {result.overall}")
print(f"检测信息: {result.overall_message}")
print(f"三码比对: {result.compare.status}")
print(f"瑕疵检测: {result.defect.status}")
```

## InspectionResult 数据类

检测结果数据结构。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `sample_id` | str | 样品编号 |
| `overall` | StepStatus | 总体判定结果 |
| `overall_message` | str | 总体判定信息 |
| `front` | StepResult | 正面QR识别结果 |
| `side` | StepResult | 侧面条码识别结果 |
| `back` | StepResult | 背面条码识别结果 |
| `compare` | CompareResult | 三码比对结果 |
| `defect` | DefectResult | 瑕疵检测结果 |

### StepResult 数据类

单个步骤的检测结果。

**属性**：
- `ok` (bool): 是否成功
- `status` (StepStatus): 状态枚举
- `message` (str): 结果消息
- `data` (str | None): 解码数据
- `annotated` (np.ndarray | None): 标注后的图像

### CompareResult 数据类

三码比对结果。

**属性**：
- `status` (StepStatus): 比对状态
- `front_qr` (str | None): 正面QR码
- `expected_barcode` (str | None): 期望条码
- `side_barcode` (str | None): 侧面条码
- `back_barcode` (str | None): 背面条码
- `mes_record` (MESRecord | None): MES记录
- `message` (str | None): 比对消息

### DefectResult 数据类

瑕疵检测结果。

**属性**：
- `status` (StepStatus): 检测状态
- `message` (str | None): 检测消息
- `boxes` (list | None): 瑕疵框列表
- `confidences` (list | None): 置信度列表
- `classes` (list | None): 类别列表
- `annotated` (np.ndarray | None): 标注后的图像

## StepStatus 枚举

检测步骤状态枚举。

```python
from pipeline import StepStatus
```

**枚举值**：
- `PASS`: 通过
- `FAIL`: 失败
- `PENDING`: 待检
- `SKIP`: 跳过

**使用示例**：
```python
if result.compare.status == StepStatus.PASS:
    print("三码比对通过")
elif result.compare.status == StepStatus.FAIL:
    print("三码比对失败")
```

## 完整示例

### 基础使用

```python
from pathlib import Path
from pipeline import InspectionPipeline, StepStatus

# 初始化
pipeline = InspectionPipeline(
    mes_path="MES-ID.cgf",
    model_path="models/best.pt"
)

# 执行检测
result = pipeline.inspect_sample_dir(Path("data"), "2")

# 判断结果
if result.overall == StepStatus.PASS:
    print("✅ 检测通过")
else:
    print("❌ 检测失败")
    print(f"原因: {result.overall_message}")
```

### 批量检测

```python
from pathlib import Path
from pipeline import InspectionPipeline
import pandas as pd

pipeline = InspectionPipeline("MES-ID.cgf", "models/best.pt")
DATA_ROOT = Path("data")

# 批量检测
results = []
for i in range(1, 11):
    result = pipeline.inspect_sample_dir(DATA_ROOT, str(i))
    
    results.append({
        "sample_id": i,
        "overall": result.overall.value,
        "qr_match": result.compare.status == StepStatus.PASS,
        "has_defect": result.defect.status == StepStatus.FAIL,
        "message": result.overall_message
    })

# 导出为CSV
df = pd.DataFrame(results)
df.to_csv("detection_results.csv", index=False)
print(f"检测结果已保存，共 {len(results)} 个样品")
```

### 自定义检测流程

```python
from pathlib import Path
from pipeline import InspectionPipeline
from QRDecode import imread_unicode, decode_qr, decode_barcode

pipeline = InspectionPipeline("MES-ID.cgf", None)  # 不使用模型
DATA_ROOT = Path("data")

# 手动执行检测步骤
sample_id = "2"

# 步骤1：读取图像
front_img = imread_unicode(DATA_ROOT / "front" / f"{sample_id}-1.jpg")
side_img = imread_unicode(DATA_ROOT / "side" / f"{sample_id}-3.jpg")
back_img = imread_unicode(DATA_ROOT / "back" / f"{sample_id}-2.jpg")

# 步骤2：解码
qr_data = decode_qr(front_img)
side_barcode = decode_barcode(side_img)
back_barcode = decode_barcode(back_img)

# 步骤3：MES查询
mes_record = pipeline.mes.query_by_qr(qr_data)

# 步骤4：三码比对
if mes_record:
    expected = mes_record.barcode
    if side_barcode == back_barcode == expected:
        print("✅ 三码比对通过")
    else:
        print(f"❌ 三码不一致: 侧面={side_barcode}, 背面={back_barcode}, 期望={expected}")
else:
    print(f"❌ MES中未找到QR码: {qr_data}")
```

## 错误处理

### 异常捕获

```python
from pipeline import InspectionPipeline
from pathlib import Path

pipeline = InspectionPipeline("MES-ID.cgf", "models/best.pt")

try:
    result = pipeline.inspect_sample_dir(Path("data"), "999")
except FileNotFoundError as e:
    print(f"样品文件不存在: {e}")
except Exception as e:
    print(f"检测异常: {e}")
```

### 日志记录

```python
import logging
from pipeline import InspectionPipeline

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

pipeline = InspectionPipeline("MES-ID.cgf", "models/best.pt")
result = pipeline.inspect_sample_dir("data", "2")
```

## 性能优化

### 使用GPU加速

```python
import torch
from pipeline import InspectionPipeline

# 检查CUDA可用性
if torch.cuda.is_available():
    print("使用GPU加速")
    model_path = "models/best.pt"
else:
    print("使用CPU模式")
    model_path = None  # 使用配置模式

pipeline = InspectionPipeline("MES-ID.cgf", model_path)
```

### 批量检测优化

```python
from pipeline import InspectionPipeline
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

pipeline = InspectionPipeline("MES-ID.cgf", "models/best.pt")
DATA_ROOT = Path("data")

def detect_sample(sample_id):
    """检测单个样品。"""
    result = pipeline.inspect_sample_dir(DATA_ROOT, sample_id)
    return sample_id, result.overall.value

# 并行检测
sample_ids = [str(i) for i in range(1, 11)]
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(detect_sample, sample_ids))

for sample_id, status in results:
    print(f"样品 {sample_id}: {status}")
```

## 参考文档

- [MES数据库API](mes-db.md)
- [QR解码API](qr-decode.md)
- [标注解析API](label-parser.md)
