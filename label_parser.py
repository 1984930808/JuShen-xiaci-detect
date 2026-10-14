"""LabelImg 标注文件解析器（PASCAL VOC 格式）。"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


class BoundingBox:
    """边界框数据类。"""
    
    def __init__(self, name: str, xmin: int, ymin: int, xmax: int, ymax: int):
        self.name = name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
    
    def to_xywh(self) -> tuple[int, int, int, int]:
        """转换为 (x, y, w, h) 格式。"""
        return (self.xmin, self.ymin, self.xmax - self.xmin, self.ymax - self.ymin)
    
    def __repr__(self) -> str:
        return f"BoundingBox({self.name}, x={self.xmin}, y={self.ymin}, w={self.xmax-self.xmin}, h={self.ymax-self.ymin})"


class LabelAnnotation:
    """标注文件数据类。"""
    
    def __init__(self, image_path: str, width: int, height: int, boxes: list[BoundingBox]):
        self.image_path = image_path
        self.width = width
        self.height = height
        self.boxes = boxes
    
    def has_defects(self) -> bool:
        """是否包含瑕疵标注。"""
        return len(self.boxes) > 0
    
    def __repr__(self) -> str:
        return f"LabelAnnotation(image={self.image_path}, boxes={len(self.boxes)})"


def parse_labelimg_xml(xml_path: str | Path) -> Optional[LabelAnnotation]:
    """
    解析 LabelImg 生成的 PASCAL VOC 格式 XML 标注文件。
    
    Args:
        xml_path: XML 标注文件路径
        
    Returns:
        LabelAnnotation 对象，解析失败返回 None
        
    XML 格式示例：
    <annotation>
        <filename>1-1.jpg</filename>
        <size>
            <width>640</width>
            <height>480</height>
        </size>
        <object>
            <name>defect</name>
            <bndbox>
                <xmin>100</xmin>
                <ymin>150</ymin>
                <xmax>200</xmax>
                <ymax>250</ymax>
            </bndbox>
        </object>
    </annotation>
    """
    xml_path = Path(xml_path)
    if not xml_path.exists():
        return None
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # 读取图像信息
        filename = root.find("filename")
        size = root.find("size")
        
        if filename is None or size is None:
            return None
        
        image_path = filename.text or ""
        width = int(size.find("width").text or 0)
        height = int(size.find("height").text or 0)
        
        # 读取所有标注框
        boxes = []
        for obj in root.findall("object"):
            name_elem = obj.find("name")
            bndbox = obj.find("bndbox")
            
            if name_elem is None or bndbox is None:
                continue
            
            name = name_elem.text or "defect"
            xmin = int(bndbox.find("xmin").text or 0)
            ymin = int(bndbox.find("ymin").text or 0)
            xmax = int(bndbox.find("xmax").text or 0)
            ymax = int(bndbox.find("ymax").text or 0)
            
            boxes.append(BoundingBox(name, xmin, ymin, xmax, ymax))
        
        return LabelAnnotation(image_path, width, height, boxes)
    
    except Exception as e:
        print(f"解析标注文件失败 {xml_path}: {e}")
        return None


def find_annotation_file(image_path: str | Path) -> Optional[Path]:
    """
    查找图像对应的标注文件。
    
    优先级：
    1. 同目录下同名 .xml 文件
    2. 同目录下 annotations/ 子目录中的同名 .xml
    3. 同目录下 labels/ 子目录中的同名 .xml
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        标注文件路径，未找到返回 None
    """
    img_path = Path(image_path)
    if not img_path.exists():
        return None
    
    # 获取不带扩展名的文件名
    stem = img_path.stem
    parent = img_path.parent
    
    # 查找候选路径
    candidates = [
        parent / f"{stem}.xml",                    # 同目录
        parent / "annotations" / f"{stem}.xml",    # annotations 子目录
        parent / "labels" / f"{stem}.xml",         # labels 子目录
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    return None


def load_annotation_for_image(image_path: str | Path) -> Optional[LabelAnnotation]:
    """
    为图像加载标注数据（自动查找标注文件）。
    
    Args:
        image_path: 图像文件路径
        
    Returns:
        LabelAnnotation 对象，未找到或解析失败返回 None
    """
    xml_path = find_annotation_file(image_path)
    if xml_path is None:
        return None
    
    return parse_labelimg_xml(xml_path)
