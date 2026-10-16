# 数据标注指南

本文档介绍如何使用 LabelImg 工具对瑕疵图像进行标注。

## 目录

- [安装 LabelImg](#安装-labelimg)
- [基本使用](#基本使用)
- [标注流程](#标注流程)
- [快捷键](#快捷键)
- [标注规范](#标注规范)
- [常见问题](#常见问题)

## 安装 LabelImg

### 方式1：通过pip安装（推荐）

```bash
pip install labelimg
```

### 方式2：下载可执行文件

访问 [LabelImg Release](https://github.com/tzutalin/labelImg/releases) 下载对应平台的安装包。

## 基本使用

### 启动LabelImg

```bash
# 方式1：命令行启动
labelimg

# 方式2：指定图像和标注目录
labelimg data/front data/front/annotations

# 方式3：使用Python模块
python -m labelimg
```

### 界面说明

```
┌─────────────────────────────────────────────┐
│  File  Edit  View  Help                     │ 菜单栏
├──────────┬──────────────────────────────────┤
│          │                                  │
│  文件列表 │         图像显示区域             │
│          │                                  │
│          │                                  │
│          │                                  │
├──────────┴──────────────────────────────────┤
│  标注列表   │ 标注详情                       │
└─────────────┴───────────────────────────────┘
```

## 标注流程

### 步骤1：打开图像目录

1. 点击 `Open Dir` 按钮
2. 选择 `data/front` 目录
3. 所有图像将显示在左侧文件列表中

### 步骤2：设置保存目录

1. 点击 `Change Save Dir` 按钮
2. 选择 `data/front/annotations` 目录
3. 标注文件将自动保存到此目录

### 步骤3：选择标注格式

**重要**：选择 PASCAL VOC 格式（`.xml`）

1. 左侧面板选择 `PascalVOC`
2. 不要选择 YOLO 格式（本项目使用VOC格式）

### 步骤4：创建标注框

1. 点击工具栏的 `Create RectBox` 按钮（或按 `W` 键）
2. 在图像上拖拽鼠标绘制矩形框
3. 松开鼠标后，输入类别名称（如 `scratch`、`stain`）
4. 点击 OK 确认

### 步骤5：保存标注

- 自动保存：每创建一个标注框后自动保存
- 手动保存：按 `Ctrl+S`（Windows/Linux）或 `Cmd+S`（macOS）

### 步骤6：切换到下一张图像

- 点击 `Next Image` 按钮
- 或按 `D` 键
- 或点击文件列表中的下一张图像

## 快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `W` | 创建矩形框 | 开始标注 |
| `A` | 上一张图像 | 向前翻页 |
| `D` | 下一张图像 | 向后翻页 |
| `Del` | 删除选中框 | 删除标注 |
| `Ctrl+S` | 保存 | 手动保存 |
| `Ctrl+U` | 打开目录 | 选择图像目录 |
| `Ctrl+R` | 更改保存目录 | 设置标注输出位置 |
| `Ctrl+D` | 复制框 | 复制当前标注框 |
| `Ctrl+H` | 隐藏/显示框 | 切换标注显示 |

## 标注规范

### 瑕疵类别命名

建议使用统一的类别名称：

| 类别名称 | 中文说明 | 示例 |
|----------|----------|------|
| `scratch` | 划痕 | 细长条状缺陷 |
| `stain` | 污渍 | 不规则色斑 |
| `dent` | 凹陷 | 局部凹陷 |
| `crack` | 裂纹 | 细小裂纹 |
| `bubble` | 气泡 | 圆形气泡 |
| `deformation` | 变形 | 形状异常 |
| `rust` | 锈蚀 | 锈斑 |
| `other` | 其他 | 其他类型 |

### 标注原则

**✅ 正确做法**：
1. 紧贴瑕疵边缘绘制框
2. 一个框只包含一个瑕疵
3. 多个瑕疵绘制多个框
4. 类别名称统一使用英文小写

**❌ 错误做法**：
1. 框过大或过小
2. 一个框包含多个瑕疵
3. 类别名称随意（如"瑕疵1"、"缺陷A"）

### 标注示例

**单个瑕疵**：
```
图像：3-1.jpg
标注：3-1.xml
内容：
  <object>
    <name>scratch</name>
    <bndbox>
      <xmin>120</xmin>
      <ymin>85</ymin>
      <xmax>280</xmax>
      <ymax>165</ymax>
    </bndbox>
  </object>
```

**多个瑕疵**：
```
图像：6-1.jpg
标注：6-1.xml
内容：包含3个瑕疵框
  - scratch: (120, 85) - (280, 165)
  - stain: (350, 200) - (420, 280)
  - dent: (200, 320) - (260, 380)
```

## 常见问题

### Q1: 标注文件保存在哪里？

**推荐位置**（按优先级）：
1. `data/front/annotations/{id}-1.xml`（推荐）
2. `data/front/{id}-1.xml`（同目录）
3. `data/front/labels/{id}-1.xml`

### Q2: 如何修改已有的标注？

1. 在标注列表中选中要修改的框
2. 拖动框的边角调整大小
3. 或删除后重新绘制（按 `Del` 键）
4. 修改后记得保存（`Ctrl+S`）

### Q3: 标注文件格式说明？

**PASCAL VOC格式（.xml）**：
```xml
<annotation>
    <folder>front</folder>
    <filename>3-1.jpg</filename>
    <path>D:\project\data\front\3-1.jpg</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>640</width>
        <height>480</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    <object>
        <name>scratch</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>120</xmin>
            <ymin>85</ymin>
            <xmax>280</xmax>
            <ymax>165</ymax>
        </bndbox>
    </object>
</annotation>
```

### Q4: 如何批量验证标注文件？

使用项目提供的验证脚本：

```python
from label_parser import LabelParser
from pathlib import Path

parser = LabelParser()
annotations_dir = Path("data/front/annotations")

for xml_file in annotations_dir.glob("*.xml"):
    result = parser.parse(xml_file)
    if result:
        print(f"✅ {xml_file.name}: {len(result['objects'])} 个瑕疵")
    else:
        print(f"❌ {xml_file.name}: 解析失败")
```

### Q5: 标注质量如何保证？

**建议流程**：
1. 一人标注，另一人复核
2. 定期抽查标注质量
3. 统一类别名称和标注标准
4. 建立标注规范文档

### Q6: 可以导出为YOLO格式吗？

可以，但本项目直接使用VOC格式。

如需导出YOLO格式：
```bash
# 在LabelImg中切换格式
View -> Auto Save mode -> YOLO
```

## 高级技巧

### 批量重命名类别

```python
import xml.etree.ElementTree as ET
from pathlib import Path

annotations_dir = Path("data/front/annotations")

for xml_file in annotations_dir.glob("*.xml"):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for obj in root.findall('object'):
        name = obj.find('name')
        # 重命名类别
        if name.text == 'old_name':
            name.text = 'new_name'
    
    tree.write(xml_file, encoding='utf-8')
```

### 统计标注信息

```python
from label_parser import LabelParser
from pathlib import Path
from collections import Counter

parser = LabelParser()
annotations_dir = Path("data/front/annotations")

category_count = Counter()
total_boxes = 0

for xml_file in annotations_dir.glob("*.xml"):
    result = parser.parse(xml_file)
    if result:
        for obj in result['objects']:
            category_count[obj['name']] += 1
            total_boxes += 1

print(f"总标注框数: {total_boxes}")
print("各类别统计:")
for category, count in category_count.most_common():
    print(f"  {category}: {count}")
```

## 参考资料

- [LabelImg 官方文档](https://github.com/tzutalin/labelImg)
- [PASCAL VOC 格式说明](http://host.robots.ox.ac.uk/pascal/VOC/)
- [数据标注最佳实践](https://docs.google.com/document/d/1O0ZinBhM8nJLd8HD3NnN4sA5-3H5p9C0/edit)
