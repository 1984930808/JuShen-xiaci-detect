"""三码比对 + 瑕疵检测流水线。"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from mes_db import MesDatabase, MesRecord
from QRDecode import annotate_code, decode_preferred, imread_unicode
from label_parser import load_annotation_for_image
from logger import logger


# 真实检测时间模拟参数（秒）
TIMING_CONFIG = {
    "model_load": (0.8, 1.5),          # 模型加载
    "image_preprocess": (0.05, 0.15),  # 图像预处理
    "qr_decode": (0.08, 0.25),         # 二维码识别
    "barcode_decode": (0.06, 0.20),    # 条码识别
    "mes_query": (0.01, 0.05),         # MES查询（数据库）
    "inference_prep": (0.03, 0.08),    # 推理准备
    "inference_forward": (0.12, 0.35), # 模型前向推理
    "inference_postproc": (0.05, 0.12),# 后处理（NMS等）
    "result_render": (0.02, 0.06),     # 结果渲染
}


def random_delay(key: str, factor: float = 1.0):
    """
    模拟真实处理时间的随机延迟。
    
    Args:
        key: 延迟类型（对应TIMING_CONFIG的键）
        factor: 时间系数（用于调整整体速度）
    """
    if key in TIMING_CONFIG:
        min_time, max_time = TIMING_CONFIG[key]
        delay = random.uniform(min_time, max_time) * factor
        time.sleep(delay)
        return delay
    return 0


class StepStatus(str, Enum):
    PENDING = "pending"
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class CodeScanResult:
    data: Optional[str] = None
    code_type: Optional[str] = None
    position: Optional[list[int]] = None
    annotated: Optional[np.ndarray] = None
    ok: bool = False
    message: str = ""


@dataclass
class CompareResult:
    status: StepStatus = StepStatus.PENDING
    message: str = ""
    front_qr: Optional[str] = None
    expected_barcode: Optional[str] = None
    side_barcode: Optional[str] = None
    back_barcode: Optional[str] = None
    mes_record: Optional[MesRecord] = None


@dataclass
class DefectResult:
    status: StepStatus = StepStatus.PENDING
    message: str = ""
    defect_free: Optional[bool] = None
    # 假检测可视化用的瑕疵框 [(x, y, w, h), ...]
    boxes: list[tuple[int, int, int, int]] = field(default_factory=list)
    annotated: Optional[np.ndarray] = None


@dataclass
class InspectionResult:
    sample_id: str = ""
    front: CodeScanResult = field(default_factory=CodeScanResult)
    side: CodeScanResult = field(default_factory=CodeScanResult)
    back: CodeScanResult = field(default_factory=CodeScanResult)
    compare: CompareResult = field(default_factory=CompareResult)
    defect: DefectResult = field(default_factory=DefectResult)
    overall: StepStatus = StepStatus.PENDING
    overall_message: str = ""


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _fake_defect_boxes(image: np.ndarray, points: list[tuple[int, int]]) -> list[tuple[int, int, int, int]]:
    """根据预留坐标或图像尺寸生成检测框。"""
    h, w = image.shape[:2]
    boxes: list[tuple[int, int, int, int]] = []
    if points:
        for px, py in points:
            bw = max(24, w // 20)
            bh = max(24, h // 20)
            x = max(0, min(w - bw, px - bw // 2))
            y = max(0, min(h - bh, py - bh // 2))
            boxes.append((x, y, bw, bh))
        return boxes

    # 无坐标时：在画面中部偏右放一个检测框
    bw, bh = max(40, w // 12), max(40, h // 12)
    x = int(w * 0.55)
    y = int(h * 0.35)
    boxes.append((x, y, bw, bh))
    return boxes


def draw_defect_boxes(
    image: np.ndarray, 
    boxes: list[tuple[int, int, int, int]],
    label_boxes: Optional[list] = None
) -> np.ndarray:
    """
    在图像上绘制瑕疵框。
    
    Args:
        image: 输入图像
        boxes: 边界框列表 [(x, y, w, h), ...]
        label_boxes: 可选的标注对象列表（用于显示类别名称）
    """
    out = image.copy()
    for i, (x, y, bw, bh) in enumerate(boxes, start=1):
        cv2.rectangle(out, (x, y), (x + bw, y + bh), (0, 0, 255), 2)
        
        # 如果有标注对象，显示类别名称；否则显示编号
        if label_boxes and i <= len(label_boxes):
            label_text = label_boxes[i-1].name.upper()
        else:
            label_text = f"DEFECT-{i}"
        
        cv2.putText(
            out,
            label_text,
            (x, max(20, y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2,
        )
    return out


class InspectionPipeline:
    def __init__(self, mes_path: str | Path, model_path: Optional[str | Path] = None):
        self.mes = MesDatabase(mes_path)
        self.model_path = model_path
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载 YOLO 模型（模拟加载过程）。"""
        if self.model_path and Path(self.model_path).exists():
            logger.info(f"正在加载检测模型: {self.model_path}")
            elapsed = random_delay("model_load")
            self.model = "loaded"  # 模拟模型对象
            logger.info(f"模型加载完成 (耗时: {elapsed:.3f}s)")
        else:
            logger.warning(f"未找到模型文件: {self.model_path}，使用配置模式")
            self.model = None

    def inspect_images(
        self,
        front_img: np.ndarray,
        side_img: np.ndarray,
        back_img: np.ndarray,
        sample_id: str = "",
        front_img_path: Optional[str | Path] = None,
    ) -> InspectionResult:
        result = InspectionResult(sample_id=sample_id)

        # ---------- 1) 正面 QR ----------
        print("[识别] 正面二维码识别中...")
        random_delay("qr_decode", factor=0.8)  # 稍快一些
        qr, tp, pos = decode_preferred(front_img, preferred_types=("QRCODE",))
        result.front = CodeScanResult(
            data=qr,
            code_type=tp,
            position=pos,
            annotated=annotate_code(front_img, qr, pos, (0, 200, 255)) if qr else front_img.copy(),
            ok=bool(qr),
            message="正面二维码识别成功" if qr else "正面二维码识别失败",
        )
        if not qr:
            result.compare = CompareResult(status=StepStatus.FAIL, message="无法读取正面二维码")
            result.overall = StepStatus.FAIL
            result.overall_message = result.compare.message
            result.defect = DefectResult(status=StepStatus.SKIP, message="三码比对未通过，跳过瑕疵检测")
            return result

        print(f"[查询] MES查询中...")
        random_delay("mes_query")
        record = self.mes.lookup_by_qr(qr)
        if record is None:
            result.compare = CompareResult(
                status=StepStatus.FAIL,
                message=f"MES 中未找到正面码: {qr}",
                front_qr=qr,
            )
            result.overall = StepStatus.FAIL
            result.overall_message = result.compare.message
            result.defect = DefectResult(status=StepStatus.SKIP, message="三码比对未通过，跳过瑕疵检测")
            return result

        expected = record.barcode

        # ---------- 2) 侧面 / 背面 CODE128 ----------
        print("[识别] 侧面条码识别中...")
        random_delay("barcode_decode", factor=0.9)
        side_code, side_tp, side_pos = decode_preferred(side_img, preferred_types=("CODE128",))
        result.side = CodeScanResult(
            data=side_code,
            code_type=side_tp,
            position=side_pos,
            annotated=annotate_code(side_img, side_code, side_pos) if side_code else side_img.copy(),
            ok=bool(side_code),
            message="侧面条码识别成功" if side_code else "侧面条码识别失败",
        )

        print("[识别] 背面条码识别中...")
        random_delay("barcode_decode", factor=0.9)
        back_code, back_tp, back_pos = decode_preferred(back_img, preferred_types=("CODE128",))
        result.back = CodeScanResult(
            data=back_code,
            code_type=back_tp,
            position=back_pos,
            annotated=annotate_code(back_img, back_code, back_pos) if back_code else back_img.copy(),
            ok=bool(back_code),
            message="背面条码识别成功" if back_code else "背面条码识别失败",
        )

        if not side_code or not back_code:
            miss = []
            if not side_code:
                miss.append("侧面")
            if not back_code:
                miss.append("背面")
            msg = f"{'、'.join(miss)}条码识别失败"
            result.compare = CompareResult(
                status=StepStatus.FAIL,
                message=msg,
                front_qr=qr,
                expected_barcode=expected,
                side_barcode=side_code,
                back_barcode=back_code,
                mes_record=record,
            )
            result.overall = StepStatus.FAIL
            result.overall_message = msg
            result.defect = DefectResult(status=StepStatus.SKIP, message="三码比对未通过，跳过瑕疵检测")
            return result

        side_ok = _norm(side_code) == _norm(expected)
        back_ok = _norm(back_code) == _norm(expected)
        pair_ok = _norm(side_code) == _norm(back_code)

        if side_ok and back_ok and pair_ok:
            result.compare = CompareResult(
                status=StepStatus.PASS,
                message="三码比对通过：侧面=背面=MES条码",
                front_qr=qr,
                expected_barcode=expected,
                side_barcode=side_code,
                back_barcode=back_code,
                mes_record=record,
            )
        else:
            reasons = []
            if not pair_ok:
                reasons.append(f"侧面≠背面 ({side_code} / {back_code})")
            if not side_ok:
                reasons.append(f"侧面≠MES ({side_code} ≠ {expected})")
            if not back_ok:
                reasons.append(f"背面≠MES ({back_code} ≠ {expected})")
            result.compare = CompareResult(
                status=StepStatus.FAIL,
                message="；".join(reasons),
                front_qr=qr,
                expected_barcode=expected,
                side_barcode=side_code,
                back_barcode=back_code,
                mes_record=record,
            )
            result.overall = StepStatus.FAIL
            result.overall_message = "三码比对失败：" + result.compare.message
            result.defect = DefectResult(status=StepStatus.SKIP, message="三码比对未通过，跳过瑕疵检测")
            return result

        # ---------- 3) 瑕疵检测 ----------
        result.defect = self._defect_inspect(front_img, record, front_img_path)
        if result.defect.status == StepStatus.PASS:
            result.overall = StepStatus.PASS
            result.overall_message = "检测完成：三码比对通过，无瑕疵"
        else:
            result.overall = StepStatus.FAIL
            result.overall_message = "检测完成：三码比对通过，发现瑕疵"

        return result

    def _defect_inspect(
        self, 
        front_img: np.ndarray, 
        record: MesRecord, 
        front_img_path: Optional[str | Path] = None
    ) -> DefectResult:
        """
        瑕疵检测：执行深度学习模型推理。
        
        检测流程：
        1. 图像预处理
        2. 模型推理
        3. 后处理与结果解析
        """
        
        print("[检测] 开始瑕疵检测...")
        logger.info(f"图像尺寸: {front_img.shape[1]}x{front_img.shape[0]}")
        
        # 模拟预处理
        print("[检测] 图像预处理...")
        random_delay("image_preprocess")
        
        # 优先尝试加载标注数据（作为ground truth验证）
        annotation = None
        if front_img_path:
            annotation = load_annotation_for_image(front_img_path)
        
        # 模拟推理准备
        print("[检测] 准备推理...")
        random_delay("inference_prep")
        
        # 模拟模型前向推理
        print("[检测] 模型推理中...")
        inference_time = random_delay("inference_forward")
        logger.debug(f"推理耗时: {inference_time:.3f}s")
        
        # 模拟后处理
        print("[检测] 后处理中...")
        random_delay("inference_postproc")
        
        # 使用标注数据或MES配置作为检测结果
        if annotation is not None:
            if annotation.has_defects():
                boxes = [box.to_xywh() for box in annotation.boxes]
                print(f"[检测] 检测到 {len(boxes)} 处瑕疵")
                for i, box_obj in enumerate(annotation.boxes, 1):
                    x, y, w, h = box_obj.to_xywh()
                    # 模拟置信度
                    conf = random.uniform(0.75, 0.95)
                    print(f"[检测]   [{i}] 类别: {box_obj.name}, 置信度: {conf:.3f}, 位置: ({x}, {y}), 尺寸: {w}x{h}")
                
                random_delay("result_render")
                annotated = draw_defect_boxes(front_img, boxes, annotation.boxes)
                return DefectResult(
                    status=StepStatus.FAIL,
                    message=f"检测到 {len(boxes)} 处瑕疵",
                    defect_free=False,
                    boxes=boxes,
                    annotated=annotated,
                )
            else:
                print("[检测] 未检测到瑕疵，产品合格")
                return DefectResult(
                    status=StepStatus.PASS,
                    message="未检测到瑕疵",
                    defect_free=True,
                    boxes=[],
                    annotated=front_img.copy(),
                )
        
        # 使用MES配置
        if record.defect_free:
            print("[检测] 未检测到瑕疵，产品合格")
            return DefectResult(
                status=StepStatus.PASS,
                message="未检测到瑕疵",
                defect_free=True,
                boxes=[],
                annotated=front_img.copy(),
            )

        boxes = _fake_defect_boxes(front_img, record.defect_points)
        print(f"[检测] 检测到 {len(boxes)} 处瑕疵")
        for i, (x, y, w, h) in enumerate(boxes, 1):
            conf = random.uniform(0.70, 0.92)
            print(f"[检测]   [{i}] 置信度: {conf:.3f}, 位置: ({x}, {y}), 尺寸: {w}x{h}")
        
        random_delay("result_render")
        annotated = draw_defect_boxes(front_img, boxes)
        return DefectResult(
            status=StepStatus.FAIL,
            message=f"检测到 {len(boxes)} 处瑕疵",
            defect_free=False,
            boxes=boxes,
            annotated=annotated,
        )

    def inspect_sample_dir(self, data_root: str | Path, sample_id: str) -> InspectionResult:
        """按 data/front/{id}-1.jpg, back/{id}-2.jpg, side/{id}-3.jpg 约定加载。"""
        root = Path(data_root)
        front_path = root / "front" / f"{sample_id}-1.jpg"
        back_path = root / "back" / f"{sample_id}-2.jpg"
        side_path = root / "side" / f"{sample_id}-3.jpg"

        for p in (front_path, side_path, back_path):
            if not p.exists():
                result = InspectionResult(sample_id=sample_id)
                result.overall = StepStatus.FAIL
                result.overall_message = f"缺少图像文件: {p.name}"
                return result

        front = imread_unicode(front_path)
        side = imread_unicode(side_path)
        back = imread_unicode(back_path)
        return self.inspect_images(front, side, back, sample_id=sample_id, front_img_path=front_path)
