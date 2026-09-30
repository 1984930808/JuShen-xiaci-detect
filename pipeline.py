"""三码比对 + 假瑕疵检测流水线。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from mes_db import MesDatabase, MesRecord
from QRDecode import annotate_code, decode_preferred, imread_unicode


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
    """根据预留坐标或图像尺寸生成假瑕疵框，用于界面演示。"""
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

    # 无坐标时：在画面中部偏右放一个演示框
    bw, bh = max(40, w // 12), max(40, h // 12)
    x = int(w * 0.55)
    y = int(h * 0.35)
    boxes.append((x, y, bw, bh))
    return boxes


def draw_defect_boxes(image: np.ndarray, boxes: list[tuple[int, int, int, int]]) -> np.ndarray:
    out = image.copy()
    for i, (x, y, bw, bh) in enumerate(boxes, start=1):
        cv2.rectangle(out, (x, y), (x + bw, y + bh), (0, 0, 255), 2)
        cv2.putText(
            out,
            f"DEFECT-{i}",
            (x, max(20, y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2,
        )
    return out


class InspectionPipeline:
    def __init__(self, mes_path: str | Path):
        self.mes = MesDatabase(mes_path)

    def inspect_images(
        self,
        front_img: np.ndarray,
        side_img: np.ndarray,
        back_img: np.ndarray,
        sample_id: str = "",
    ) -> InspectionResult:
        result = InspectionResult(sample_id=sample_id)

        # ---------- 1) 正面 QR ----------
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
        side_code, side_tp, side_pos = decode_preferred(side_img, preferred_types=("CODE128",))
        result.side = CodeScanResult(
            data=side_code,
            code_type=side_tp,
            position=side_pos,
            annotated=annotate_code(side_img, side_code, side_pos) if side_code else side_img.copy(),
            ok=bool(side_code),
            message="侧面条码识别成功" if side_code else "侧面条码识别失败",
        )

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

        # ---------- 3) 假瑕疵检测（表面完整） ----------
        result.defect = self._fake_defect_inspect(front_img, record)
        if result.defect.status == StepStatus.PASS:
            result.overall = StepStatus.PASS
            result.overall_message = "检测完成：三码比对通过，无瑕疵"
        else:
            result.overall = StepStatus.FAIL
            result.overall_message = "检测完成：三码比对通过，发现瑕疵"

        return result

    def _fake_defect_inspect(self, front_img: np.ndarray, record: MesRecord) -> DefectResult:
        """假瑕疵检测：按 MES 第三列判定，并绘制演示标注。"""
        if record.defect_free:
            return DefectResult(
                status=StepStatus.PASS,
                message="瑕疵检测通过（无瑕疵）",
                defect_free=True,
                boxes=[],
                annotated=front_img.copy(),
            )

        boxes = _fake_defect_boxes(front_img, record.defect_points)
        annotated = draw_defect_boxes(front_img, boxes)
        return DefectResult(
            status=StepStatus.FAIL,
            message=f"瑕疵检测未通过（发现 {len(boxes)} 处瑕疵，演示结果）",
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
        return self.inspect_images(front, side, back, sample_id=sample_id)
