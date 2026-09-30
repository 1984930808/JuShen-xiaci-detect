"""MES-ID 数据库加载与查询。

文件格式（每行）：正面QR码,侧面/背面条码,瑕疵标记
瑕疵标记：1=无瑕疵，0=有瑕疵（后续可扩展瑕疵坐标）
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class MesRecord:
    qr_code: str
    barcode: str
    defect_free: bool  # True=无瑕疵(1), False=有瑕疵(0)
    # 预留：后续可写入瑕疵坐标 [(x, y), ...]
    defect_points: list[tuple[int, int]]


class MesDatabase:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._by_qr: dict[str, MesRecord] = {}
        self.reload()

    def reload(self) -> None:
        self._by_qr.clear()
        if not self.path.exists():
            raise FileNotFoundError(f"MES 文件不存在: {self.path}")

        with self.path.open("r", encoding="utf-8") as f:
            for lineno, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 3:
                    continue
                qr, barcode, flag = parts[0], parts[1], parts[2]
                if not qr:
                    continue
                points: list[tuple[int, int]] = []
                # 预留扩展：第4列起可为 x:y 坐标对
                for extra in parts[3:]:
                    if ":" in extra:
                        xs, ys = extra.split(":", 1)
                        try:
                            points.append((int(xs), int(ys)))
                        except ValueError:
                            pass
                record = MesRecord(
                    qr_code=qr,
                    barcode=barcode,
                    defect_free=(flag == "1"),
                    defect_points=points,
                )
                self._by_qr[qr.lower()] = record

    def lookup_by_qr(self, qr_code: str) -> Optional[MesRecord]:
        if not qr_code:
            return None
        return self._by_qr.get(qr_code.strip().lower())

    def __len__(self) -> int:
        return len(self._by_qr)
