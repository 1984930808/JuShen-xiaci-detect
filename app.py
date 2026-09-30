"""巨神瑕疵检测 — 三码比对 + 瑕疵检测界面。"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import cv2
from PIL import Image, ImageTk

from pipeline import InspectionPipeline, InspectionResult, StepStatus
from QRDecode import imread_unicode

ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data"
MES_PATH = ROOT / "MES-ID.cgf"

# 工业检测台风格
COLORS = {
    "bg": "#1a2332",
    "panel": "#243044",
    "panel_alt": "#2c3a4f",
    "border": "#3d4f66",
    "text": "#e8eef6",
    "muted": "#8fa3b8",
    "accent": "#2ea8ff",
    "pass": "#2ecc71",
    "fail": "#e74c3c",
    "pending": "#f39c12",
    "skip": "#7f8c8d",
}


def status_color(status: StepStatus) -> str:
    return {
        StepStatus.PASS: COLORS["pass"],
        StepStatus.FAIL: COLORS["fail"],
        StepStatus.PENDING: COLORS["pending"],
        StepStatus.SKIP: COLORS["skip"],
    }.get(status, COLORS["muted"])


def status_text(status: StepStatus) -> str:
    return {
        StepStatus.PASS: "通过",
        StepStatus.FAIL: "失败",
        StepStatus.PENDING: "待检",
        StepStatus.SKIP: "跳过",
    }.get(status, str(status))


class ImagePanel(ttk.Frame):
    def __init__(self, master, title: str, width: int = 320, height: int = 240):
        super().__init__(master, style="Panel.TFrame")
        self.view_w = width
        self.view_h = height
        self._photo = None

        head = ttk.Frame(self, style="Panel.TFrame")
        head.pack(fill="x", padx=8, pady=(8, 4))
        self.title_lbl = ttk.Label(head, text=title, style="Title.TLabel")
        self.title_lbl.pack(side="left")
        self.badge = tk.Label(
            head,
            text="待检",
            bg=COLORS["pending"],
            fg="#111",
            font=("Microsoft YaHei UI", 9, "bold"),
            padx=8,
            pady=1,
        )
        self.badge.pack(side="right")

        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg="#0f1620",
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.canvas.pack(padx=8, pady=4)

        self.info = ttk.Label(self, text="—", style="Muted.TLabel", wraplength=width)
        self.info.pack(fill="x", padx=8, pady=(0, 8))

    def set_badge(self, text: str, color: str):
        self.badge.configure(text=text, bg=color)

    def show_bgr(self, image_bgr, caption: str = ""):
        if image_bgr is None:
            self.canvas.delete("all")
            self.canvas.create_text(
                self.view_w // 2,
                self.view_h // 2,
                text="无图像",
                fill=COLORS["muted"],
                font=("Microsoft YaHei UI", 12),
            )
            self.info.configure(text=caption or "—")
            return

        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        scale = min(self.view_w / w, self.view_h / h)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        resized = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_AREA)
        pil = Image.fromarray(resized)
        self._photo = ImageTk.PhotoImage(pil)
        self.canvas.delete("all")
        self.canvas.create_image(self.view_w // 2, self.view_h // 2, image=self._photo)
        self.info.configure(text=caption or "—")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("具身智能瑕疵检测 · 三码比对")
        self.geometry("1180x760")
        self.minsize(1000, 680)
        self.configure(bg=COLORS["bg"])

        self.pipeline = InspectionPipeline(MES_PATH)
        self.sample_ids = self._discover_samples()
        self.current_result: InspectionResult | None = None

        self._setup_styles()
        self._build_ui()

        if self.sample_ids:
            self.sample_var.set(self.sample_ids[0])
            self.load_preview()

    def _discover_samples(self) -> list[str]:
        front_dir = DATA_ROOT / "front"
        if not front_dir.exists():
            return []
        ids = []
        for p in sorted(front_dir.glob("*-1.jpg"), key=lambda x: self._sample_sort_key(x.stem)):
            sid = p.stem.rsplit("-", 1)[0]
            ids.append(sid)
        return ids

    @staticmethod
    def _sample_sort_key(stem: str):
        sid = stem.rsplit("-", 1)[0]
        try:
            return (0, int(sid))
        except ValueError:
            return (1, sid)

    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Root.TFrame", background=COLORS["bg"])
        style.configure("Panel.TFrame", background=COLORS["panel"])
        style.configure("Alt.TFrame", background=COLORS["panel_alt"])
        style.configure(
            "Title.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Microsoft YaHei UI", 11, "bold"),
        )
        style.configure(
            "Head.TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Microsoft YaHei UI", 16, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
        )
        style.configure(
            "Body.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Microsoft YaHei UI", 10),
        )
        style.configure(
            "Result.TLabel",
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            font=("Microsoft YaHei UI", 12, "bold"),
        )
        style.configure(
            "Accent.TButton",
            font=("Microsoft YaHei UI", 11, "bold"),
            padding=(16, 8),
        )
        style.configure(
            "TCombobox",
            fieldbackground="#0f1620",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
        )

    def _build_ui(self):
        root = ttk.Frame(self, style="Root.TFrame")
        root.pack(fill="both", expand=True, padx=16, pady=12)

        # 顶栏
        top = ttk.Frame(root, style="Root.TFrame")
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="巨神瑕疵检测", style="Head.TLabel").pack(side="left")
        ttk.Label(
            top,
            text="  流程：正面QR → MES查表 → 侧面/背面条码比对 → 瑕疵检测",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
        ).pack(side="left", padx=(12, 0))

        ctrl = ttk.Frame(top, style="Root.TFrame")
        ctrl.pack(side="right")
        ttk.Label(
            ctrl,
            text="样品编号",
            background=COLORS["bg"],
            foreground=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
        ).pack(side="left", padx=(0, 6))
        self.sample_var = tk.StringVar()
        self.sample_box = ttk.Combobox(
            ctrl,
            textvariable=self.sample_var,
            values=self.sample_ids,
            width=8,
            state="readonly",
        )
        self.sample_box.pack(side="left")
        self.sample_box.bind("<<ComboboxSelected>>", lambda _e: self.load_preview())

        ttk.Button(ctrl, text="上一张", command=self.prev_sample).pack(side="left", padx=6)
        ttk.Button(ctrl, text="下一张", command=self.next_sample).pack(side="left")
        ttk.Button(ctrl, text="开始检测", style="Accent.TButton", command=self.run_inspect).pack(
            side="left", padx=(12, 0)
        )

        # 三图区
        images = ttk.Frame(root, style="Root.TFrame")
        images.pack(fill="both", expand=True)
        images.columnconfigure(0, weight=1)
        images.columnconfigure(1, weight=1)
        images.columnconfigure(2, weight=1)

        self.front_panel = ImagePanel(images, "正面 · QR Code", 340, 260)
        self.side_panel = ImagePanel(images, "侧面 · Code128", 340, 260)
        self.back_panel = ImagePanel(images, "背面 · Code128", 340, 260)
        self.front_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.side_panel.grid(row=0, column=1, sticky="nsew", padx=4)
        self.back_panel.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        # 结果区
        bottom = ttk.Frame(root, style="Alt.TFrame")
        bottom.pack(fill="x", pady=(12, 0))

        left = ttk.Frame(bottom, style="Alt.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        ttk.Label(left, text="检测结果", style="Result.TLabel").pack(anchor="w")
        self.overall_badge = tk.Label(
            left,
            text="待检",
            bg=COLORS["pending"],
            fg="#111",
            font=("Microsoft YaHei UI", 14, "bold"),
            padx=18,
            pady=6,
        )
        self.overall_badge.pack(anchor="w", pady=(8, 10))

        self.detail_text = tk.Text(
            left,
            height=8,
            wrap="word",
            bg="#0f1620",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            font=("Consolas", 10),
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        self.detail_text.pack(fill="both", expand=True)
        self.detail_text.configure(state="disabled")

        right = ttk.Frame(bottom, style="Alt.TFrame")
        right.pack(side="right", fill="y", padx=12, pady=12)

        self.step_vars = {}
        for key, title in [
            ("front", "① 正面二维码"),
            ("mes", "② MES 查表"),
            ("side_back", "③ 侧面/背面比对"),
            ("defect", "④ 瑕疵检测"),
        ]:
            row = ttk.Frame(right, style="Alt.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(
                row,
                text=title,
                background=COLORS["panel_alt"],
                foreground=COLORS["text"],
                font=("Microsoft YaHei UI", 10),
                width=16,
            ).pack(side="left")
            badge = tk.Label(
                row,
                text="待检",
                bg=COLORS["pending"],
                fg="#111",
                font=("Microsoft YaHei UI", 9, "bold"),
                width=6,
                padx=6,
            )
            badge.pack(side="left", padx=8)
            self.step_vars[key] = badge

        mes_info = ttk.Label(
            right,
            text=f"MES 记录数：{len(self.pipeline.mes)}",
            background=COLORS["panel_alt"],
            foreground=COLORS["muted"],
            font=("Microsoft YaHei UI", 9),
        )
        mes_info.pack(anchor="w", pady=(16, 0))

    def _current_index(self) -> int:
        sid = self.sample_var.get()
        if sid in self.sample_ids:
            return self.sample_ids.index(sid)
        return 0

    def prev_sample(self):
        if not self.sample_ids:
            return
        idx = (self._current_index() - 1) % len(self.sample_ids)
        self.sample_var.set(self.sample_ids[idx])
        self.load_preview()

    def next_sample(self):
        if not self.sample_ids:
            return
        idx = (self._current_index() + 1) % len(self.sample_ids)
        self.sample_var.set(self.sample_ids[idx])
        self.load_preview()

    def _read_triple(self, sample_id: str):
        front = imread_unicode(DATA_ROOT / "front" / f"{sample_id}-1.jpg")
        side = imread_unicode(DATA_ROOT / "side" / f"{sample_id}-3.jpg")
        back = imread_unicode(DATA_ROOT / "back" / f"{sample_id}-2.jpg")
        return front, side, back

    def load_preview(self):
        sid = self.sample_var.get()
        if not sid:
            return
        front, side, back = self._read_triple(sid)
        self.front_panel.show_bgr(front, f"样品 {sid} · 正面原图")
        self.side_panel.show_bgr(side, f"样品 {sid} · 侧面原图")
        self.back_panel.show_bgr(back, f"样品 {sid} · 背面原图")
        for panel in (self.front_panel, self.side_panel, self.back_panel):
            panel.set_badge("待检", COLORS["pending"])
        for badge in self.step_vars.values():
            badge.configure(text="待检", bg=COLORS["pending"])
        self.overall_badge.configure(text="待检", bg=COLORS["pending"])
        self._set_detail(f"已加载样品 {sid}，点击「开始检测」执行三码比对与瑕疵检测。")

    def _set_step(self, key: str, status: StepStatus):
        self.step_vars[key].configure(text=status_text(status), bg=status_color(status))

    def _set_detail(self, text: str):
        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.configure(state="disabled")

    def run_inspect(self):
        sid = self.sample_var.get()
        if not sid:
            messagebox.showwarning("提示", "没有可检测的样品")
            return

        try:
            result = self.pipeline.inspect_sample_dir(DATA_ROOT, sid)
        except Exception as exc:
            messagebox.showerror("检测异常", str(exc))
            return

        self.current_result = result
        self._render_result(result)

    def _render_result(self, result: InspectionResult):
        # 图像
        front_img = result.defect.annotated if result.defect.annotated is not None else result.front.annotated
        self.front_panel.show_bgr(
            front_img,
            result.front.message + (f" → {result.front.data}" if result.front.data else ""),
        )
        self.side_panel.show_bgr(
            result.side.annotated,
            result.side.message + (f" → {result.side.data}" if result.side.data else ""),
        )
        self.back_panel.show_bgr(
            result.back.annotated,
            result.back.message + (f" → {result.back.data}" if result.back.data else ""),
        )

        self.front_panel.set_badge(
            status_text(StepStatus.PASS if result.front.ok else StepStatus.FAIL),
            status_color(StepStatus.PASS if result.front.ok else StepStatus.FAIL),
        )
        self.side_panel.set_badge(
            status_text(StepStatus.PASS if result.side.ok else StepStatus.FAIL),
            status_color(StepStatus.PASS if result.side.ok else StepStatus.FAIL),
        )
        self.back_panel.set_badge(
            status_text(StepStatus.PASS if result.back.ok else StepStatus.FAIL),
            status_color(StepStatus.PASS if result.back.ok else StepStatus.FAIL),
        )

        # 步骤灯
        self._set_step("front", StepStatus.PASS if result.front.ok else StepStatus.FAIL)
        if result.compare.mes_record is not None:
            self._set_step("mes", StepStatus.PASS)
        elif result.front.ok:
            self._set_step("mes", StepStatus.FAIL)
        else:
            self._set_step("mes", StepStatus.SKIP)

        if result.compare.status == StepStatus.PASS:
            self._set_step("side_back", StepStatus.PASS)
        elif result.compare.status == StepStatus.FAIL and result.compare.expected_barcode:
            self._set_step("side_back", StepStatus.FAIL)
        elif result.compare.mes_record is None:
            self._set_step("side_back", StepStatus.SKIP)
        else:
            self._set_step("side_back", result.compare.status)

        self._set_step("defect", result.defect.status)

        self.overall_badge.configure(
            text=status_text(result.overall),
            bg=status_color(result.overall),
        )

        c = result.compare
        d = result.defect
        lines = [
            f"样品编号     : {result.sample_id}",
            f"总体结论     : {status_text(result.overall)}  —  {result.overall_message}",
            "",
            f"正面 QR      : {c.front_qr or result.front.data or '—'}",
            f"MES 期望条码 : {c.expected_barcode or '—'}",
            f"侧面 Code128 : {c.side_barcode or result.side.data or '—'}",
            f"背面 Code128 : {c.back_barcode or result.back.data or '—'}",
            f"三码比对     : {status_text(c.status)}  —  {c.message or '—'}",
            "",
            f"瑕疵检测     : {status_text(d.status)}  —  {d.message or '—'}",
        ]
        if d.boxes:
            lines.append(f"瑕疵框(演示) : {d.boxes}")
        self._set_detail("\n".join(lines))


def main():
    if not MES_PATH.exists():
        raise SystemExit(f"找不到 MES 文件: {MES_PATH}")
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
