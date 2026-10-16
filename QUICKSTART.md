# 快速开始指南

**5分钟快速体验 JuShen 瑕疵检测系统**

## 前提条件

- Python 3.8 或更高版本
- Windows/Linux/macOS

## 快速安装

```bash
# 1. 克隆项目
git clone https://github.com/1984930808/JuShen-xiaci-detect.git
cd JuShen-xiaci-detect

# 2. 创建虚拟环境（推荐）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证安装
python scripts/verify_installation.py
```

## 运行演示

```bash
# 启动检测软件
python app.py
```

系统会自动显示启动画面，然后打开主界面。

## 使用步骤

### 1. 选择样品

在界面右上角下拉框中选择样品编号（如 `2`），系统会自动加载三视角图像预览。

### 2. 执行检测

点击「开始检测」按钮，系统会自动执行：

1. **正面QR码识别**
2. **MES查表**
3. **侧面/背面条码比对**
4. **瑕疵检测**

### 3. 查看结果

检测完成后，界面显示：

- ✅ 三个视角的标注图像
- ✅ 四个步骤的状态灯（通过/失败）
- ✅ 总体判定（PASS/FAIL）
- ✅ 详细检测报告
- ✅ 完整检测日志

## 演示样品说明

项目提供 **10 个演示样品**（编号 1-10）：

| 样品ID | 三码比对 | 瑕疵检测 | 总体结果 | 说明 |
|--------|----------|----------|----------|------|
| 2 | ✅ 通过 | ✅ 无瑕疵 | **PASS** | 完整通过示例 |
| 3 | ✅ 通过 | ❌ 3处瑕疵 | **FAIL** | 瑕疵检测示例 |
| 6 | ✅ 通过 | ❌ 1处瑕疵 | **FAIL** | 单瑕疵示例 |
| 其他 | ✅ 通过 | ✅ 无瑕疵 | **PASS** | 正常样品 |

## 下一步

### 添加自定义样品

1. 准备三视角图像：
   ```
   data/front/{id}-1.jpg  # 正面
   data/side/{id}-3.jpg   # 侧面
   data/back/{id}-2.jpg   # 背面
   ```

2. 更新 MES 数据库：
   编辑 `MES-ID.cgf`，添加：
   ```text
   {正面QR码},{期望条码},1
   ```

3. 刷新样品列表（菜单栏 → 文件 → 刷新样品列表）

### 标注瑕疵

如果要模拟瑕疵检测结果：

```bash
# 安装标注工具
pip install labelimg

# 启动标注
labelimg data/front data/front/annotations
```

详细教程：[数据标注指南](docs/dataset/labeling.md)

### 训练自定义模型

```bash
# 准备YOLO格式数据集
# 配置 yolo_dataset_split/data.yaml

# 训练模型
python train.py

# 使用训练好的模型
cp runs/jushenzhineng/weights/best.pt models/best.pt
```

## 常见问题

### Q: 模型文件缺失提示？

**这是正常的**，系统有两种运行模式：

- **配置模式**（无模型文件）：基于LabelImg标注文件模拟检测
- **模型模式**（有模型文件）：真实的YOLO推理

### Q: QR码识别失败？

检查：
- 图像是否清晰
- 光照是否充足
- QR码是否完整

### Q: 检测速度慢？

- 使用GPU加速（需要CUDA）
- CPU模式也能运行，只是速度较慢

## 获取帮助

- 📚 [完整文档](docs/README.md)
- 🐛 [提交Issue](https://github.com/1984930808/JuShen-xiaci-detect/issues)
- 💬 [参与讨论](https://github.com/1984930808/JuShen-xiaci-detect/discussions)

## 许可证

本项目采用 MIT License 开源许可证。详见 [LICENSE](LICENSE) 文件。
