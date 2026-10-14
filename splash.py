"""启动画面模块。"""

import tkinter as tk
from tkinter import ttk
import time
import random


class SplashScreen:
    """系统启动画面。"""
    
    def __init__(self, duration: float = 2.5):
        self.duration = duration
        self.root = tk.Tk()
        self.root.title("")
        self.root.overrideredirect(True)  # 无边框
        
        # 窗口尺寸
        width, height = 500, 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # 背景
        self.root.configure(bg="#1a2332")
        
        # 标题
        title = tk.Label(
            self.root,
            text="具身智能瑕疵检测系统",
            font=("Microsoft YaHei UI", 20, "bold"),
            fg="#e8eef6",
            bg="#1a2332",
        )
        title.pack(pady=(60, 10))
        
        # 副标题
        subtitle = tk.Label(
            self.root,
            text="JuShen Defect Inspection System",
            font=("Arial", 10),
            fg="#8fa3b8",
            bg="#1a2332",
        )
        subtitle.pack(pady=(0, 40))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.root,
            variable=self.progress_var,
            maximum=100,
            length=350,
            mode='determinate',
        )
        self.progress.pack(pady=20)
        
        # 状态文本
        self.status = tk.Label(
            self.root,
            text="正在初始化系统...",
            font=("Microsoft YaHei UI", 9),
            fg="#8fa3b8",
            bg="#1a2332",
        )
        self.status.pack(pady=10)
        
        # 版本信息
        version = tk.Label(
            self.root,
            text="Version 1.2.0 | Powered by YOLOv11",
            font=("Arial", 8),
            fg="#5a6a7a",
            bg="#1a2332",
        )
        version.pack(side="bottom", pady=10)
    
    def update_progress(self, value: float, status: str):
        """更新进度。"""
        self.progress_var.set(value)
        self.status.configure(text=status)
        self.root.update()
    
    def show(self):
        """显示启动画面并模拟加载过程。"""
        # 模拟加载步骤
        steps = [
            (10, "加载配置文件..."),
            (25, "初始化数据库连接..."),
            (40, "加载 MES 映射表..."),
            (55, "检测 CUDA 环境..."),
            (70, "加载 YOLO 模型..."),
            (85, "初始化检测流水线..."),
            (100, "启动完成！"),
        ]
        
        start_time = time.time()
        
        for progress, status in steps:
            self.update_progress(progress, status)
            # 随机延迟，模拟真实加载
            delay = random.uniform(0.15, 0.35)
            time.sleep(delay)
        
        # 确保至少显示指定时长
        elapsed = time.time() - start_time
        if elapsed < self.duration:
            time.sleep(self.duration - elapsed)
        
        self.root.destroy()


def show_splash(duration: float = 2.5):
    """显示启动画面。"""
    splash = SplashScreen(duration)
    splash.show()


if __name__ == "__main__":
    show_splash()
