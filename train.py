"""YOLOv11 训练入口脚本。"""

from __future__ import annotations

from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent
DATA_YAML = ROOT / "yolo_dataset_split" / "data.yaml"
MODEL_PATH = ROOT / "runs" / "detect" / "yolo11_train3" / "weights" / "best.pt"  # 之前训练出的模型


def main() -> None:
    # 检查数据集配置文件是否存在
    if not DATA_YAML.exists():
        raise FileNotFoundError(
            f"未找到 {DATA_YAML}，请先运行数据集准备脚本"
        )

    # 检查模型文件是否存在
    if not MODEL_PATH.exists():
        print(f"警告: 未找到 {MODEL_PATH}，将使用预训练模型 yolo11n.pt")
        model_path = "yolo11n.pt"
    else:
        model_path = str(MODEL_PATH)
        print(f"使用之前训练的模型: {model_path}")

    # 加载模型
    model = YOLO(model_path)

    # 开始训练 - 根据YOLO官网推荐的参数设置
    model.train(
        data=str(DATA_YAML),  # 数据集配置文件
        epochs=500,  # 训练轮数
        patience=30,  # 验证指标无改善的等待周期数
        imgsz=640,  # 输入图像尺寸
        batch=16,  # 批次大小，可根据显存调整
        amp=True,   #True 或 "fp16" 使用 FP16
        device="0",  # 使用GPU训练
        workers=4,  # 数据加载线程数
        project=str(ROOT / "runs" / "jushenzhineng"),  # 输出目录
        name="zhineng_train",  # 实验名称

        resume=False,  # 从中断处继续训练
        pretrained=True,  # 使用预训练权重`
        optimizer="auto",  # 自动选择优化器（长训练会自动使用MuSGD）
        # cls_remap=True,                     # 重新映射类别标签
        save=True,  # 保存训练检查点和最终模型
        save_period=-1,  # 保存周期数
        plots=True,  # 生成训练和验证指标图
        val=True,  # 启用验证
        cache=False,  # 将数据集图像缓存到内存以提高训练速度
        seed=42,  # 随机种子，确保可复现性
        verbose=True,

        time=None,  # 最大训练时间（小时） float
        hsv_h=0.005,  # 色调随机调整范围
        hsv_s=0.5,  # 饱和度随机调整范围
        hsv_v=0.3,  # 亮度随机调整范围
        degrees=0.0,  # 随机旋转角度范围
        translate=0.1,  # 随机平移范围
        scale=0.25,  # 随机缩放范围
        shear=0.0,  # 随机剪切范围
        perspective=0.0,  # 随机透视变换范围
        flipud=0.0,  # 上下翻转范围
        fliplr=0.5,  # 左右翻转范围
        bgr=0,  # 是否将图像转换为BGR格式
        mosaic=1.0,  # 马赛克增强概率
        close_mosaic=50,  # 最后50个周期禁用马赛克增强
        mixup=0,  # 混合增强概率
        cutmix=0,  # 剪切混合增强概率
        copy_paste=0,  # 复制粘贴增强概率
        erasing=0.4,  # 擦除增强概率
        box=6.0,  # 损失函数中框损失分量的权重
        cls=0.75,  # 总损失函数中的分类损失权重
        # copy_paste_mode="",  # 指定要使用的 copy-paste 策略，选项包括 'flip' 和 'mixup'。
        # auto_augment="" #分类专用增强
        # augmentations=None,  # 用于高级数据增强的自定义 Albumentations 变换
    )


if __name__ == "__main__":
    main()