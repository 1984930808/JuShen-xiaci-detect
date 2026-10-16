# MES Database API 文档

本文档介绍MES数据库查询接口。

## MESDatabase 类

MES数据库管理类，负责加载和查询MES映射表。

### 初始化

```python
from mes_db import MESDatabase

mes = MESDatabase("MES-ID.cgf")
```

**参数**：
- `mes_path` (str | Path): MES配置文件路径

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `records` | dict[str, MESRecord] | MES记录字典（QR码 → 记录） |
| `mes_path` | Path | MES文件路径 |

### 方法

#### query_by_qr

通过QR码查询MES记录。

```python
record = mes.query_by_qr("qjG8o3TPd1Z")
```

**参数**：
- `qr_code` (str): QR码内容

**返回**：`MESRecord` 对象或 `None`

**示例**：
```python
from mes_db import MESDatabase

mes = MESDatabase("MES-ID.cgf")

# 查询记录
record = mes.query_by_qr("qjG8o3TPd1Z")

if record:
    print(f"QR码: {record.qr_code}")
    print(f"条码: {record.barcode}")
    print(f"质检标记: {record.quality_mark}")
    print(f"瑕疵点: {record.defect_points}")
else:
    print("未找到记录")
```

#### query_by_barcode

通过条码查询MES记录（返回第一个匹配）。

```python
records = mes.query_by_barcode("9C0EA9EC")
```

**参数**：
- `barcode` (str): 条码内容

**返回**：`MESRecord` 对象或 `None`

## MESRecord 数据类

MES记录数据结构。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `qr_code` | str | 正面QR码 |
| `barcode` | str | 侧面/背面条码 |
| `quality_mark` | int | 质检标记（1=良品, 0=不良） |
| `defect_points` | list[tuple[int, int]] | 瑕疵点坐标列表 |

### 使用示例

```python
from mes_db import MESDatabase

mes = MESDatabase("MES-ID.cgf")

# 遍历所有记录
for qr_code, record in mes.records.items():
    print(f"QR: {record.qr_code}, 条码: {record.barcode}, 质检: {record.quality_mark}")
    
# 统计良品和不良品
good_count = sum(1 for r in mes.records.values() if r.quality_mark == 1)
bad_count = sum(1 for r in mes.records.values() if r.quality_mark == 0)

print(f"良品: {good_count}, 不良品: {bad_count}")
```

## MES文件格式

### 格式说明

```text
正面QR码,侧面背面条码,质检标记[,x:y,...]
```

| 字段 | 必需 | 说明 | 示例 |
|------|------|------|------|
| 正面QR | ✅ | 工件主ID | `qjG8o3TPd1Z` |
| 条码 | ✅ | 侧面/背面Code128 | `9C0EA9EC` |
| 质检标记 | ✅ | 1=良品, 0=不良 | `1` |
| x:y | ❌ | 瑕疵点坐标 | `320:180` |

### 示例文件

```text
qjG8o3TPd1Z,9C0EA9EC,1
OqfSJH6wKG5,842ccafd,0,320:180,450:200
PROD003,BC003,1
PROD004,BC004,0,100:50,200:150,300:250
```

## 完整示例

### 基础查询

```python
from mes_db import MESDatabase

# 加载MES数据库
mes = MESDatabase("MES-ID.cgf")

# 查询单个记录
qr_code = "qjG8o3TPd1Z"
record = mes.query_by_qr(qr_code)

if record:
    print(f"找到记录:")
    print(f"  QR码: {record.qr_code}")
    print(f"  条码: {record.barcode}")
    print(f"  质检标记: {'良品' if record.quality_mark == 1 else '不良品'}")
    
    if record.defect_points:
        print(f"  瑕疵点: {record.defect_points}")
else:
    print(f"未找到QR码为 {qr_code} 的记录")
```

### 批量验证

```python
from mes_db import MESDatabase
from pathlib import Path

mes = MESDatabase("MES-ID.cgf")

# 验证所有记录都有必需字段
errors = []
for qr_code, record in mes.records.items():
    if not record.qr_code:
        errors.append(f"{qr_code}: QR码为空")
    if not record.barcode:
        errors.append(f"{qr_code}: 条码为空")
    if record.quality_mark not in [0, 1]:
        errors.append(f"{qr_code}: 质检标记无效")

if errors:
    print("发现错误:")
    for error in errors:
        print(f"  ❌ {error}")
else:
    print("✅ 所有MES记录格式正确")
```

### 数据统计

```python
from mes_db import MESDatabase
from collections import Counter

mes = MESDatabase("MES-ID.cgf")

# 统计质量分布
quality_dist = Counter(r.quality_mark for r in mes.records.values())

print("质量分布:")
print(f"  良品: {quality_dist[1]}")
print(f"  不良品: {quality_dist[0]}")

# 统计瑕疵数量
defect_counts = Counter(len(r.defect_points) for r in mes.records.values())

print("\n瑕疵数量分布:")
for count, num_records in sorted(defect_counts.items()):
    print(f"  {count}个瑕疵: {num_records}个样品")
```

### 导出数据

```python
from mes_db import MESDatabase
import pandas as pd

mes = MESDatabase("MES-ID.cgf")

# 转换为DataFrame
data = []
for record in mes.records.values():
    data.append({
        "qr_code": record.qr_code,
        "barcode": record.barcode,
        "quality_mark": record.quality_mark,
        "defect_count": len(record.defect_points)
    })

df = pd.DataFrame(data)
df.to_csv("mes_export.csv", index=False)
print(f"已导出 {len(df)} 条MES记录")
```

## 错误处理

### 文件不存在

```python
from mes_db import MESDatabase

try:
    mes = MESDatabase("nonexistent.cgf")
except FileNotFoundError:
    print("MES文件不存在")
```

### 格式错误

```python
from mes_db import MESDatabase

try:
    mes = MESDatabase("MES-ID.cgf")
except ValueError as e:
    print(f"MES文件格式错误: {e}")
```

## 性能考虑

### 内存占用

- 每条记录约占用100-200字节
- 1万条记录约占用1-2MB内存
- 适合在内存中加载整个数据库

### 查询速度

- `query_by_qr`: O(1)，字典查找
- `query_by_barcode`: O(n)，需要遍历

**优化建议**：
- 如果频繁按条码查询，可建立反向索引
- 大规模数据考虑使用SQLite数据库

## 参考文档

- [Pipeline API](pipeline.md)
- [快速入门](../quick-start.md)
