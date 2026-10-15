# 安装指南

本指南将帮助您在本地环境安装和配置 JuShen 瑕疵检测系统。

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | Intel i5 或同等性能 | Intel i7 或更高 |
| 内存 | 8GB RAM | 16GB RAM 或更高 |
| 存储 | 10GB 可用空间 | 50GB SSD |
| GPU | 无（CPU可运行） | NVIDIA GPU (CUDA 11.0+) |

### 软件要求

- **操作系统**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.8 - 3.11 (推荐 3.10)
- **Git**: 用于克隆代码仓库
- **CUDA**: 11.0+ (可选，GPU加速)

## 安装步骤

### 1. 克隆项目

```bash
# 使用 HTTPS
git clone https://github.com/1984930808/JuShen-xiaci-detect.git

# 或使用 SSH
git clone git@github.com:1984930808/JuShen-xiaci-detect.git

# 进入项目目录
cd JuShen-xiaci-detect
```

### 2. 创建虚拟环境

**方式1：使用 Conda（推荐）**

```bash
# 创建环境
conda create -n jushen python=3.10

# 激活环境
conda activate jushen
```

**方式2：使用 venv**

```bash
# 创建环境
python -m venv venv

# 激活环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 如果使用 GPU（可选）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**requirements.txt 内容**：
```
opencv-python>=4.8
numpy>=1.24
pyzbar>=0.1.9
Pillow>=10.0
ultralytics>=8.3.0
```

### 4. 验证安装

```bash
# 检查依赖
python system_info.py

# 期望输出
# ============================================================
# 系统信息
# ============================================================
# 系统          : Windows
# Python版本    : 3.10.x
# OpenCV版本    : 4.8.x
# NumPy版本     : 1.24.x
# PyTorch版本   : 2.x.x
# YOLO版本      : 8.3.x
# ============================================================
```

### 5. 配置 MES 数据库

编辑 `MES-ID.cgf` 文件，添加您的产品映射关系：

```text
正面QR码,条码,质检标记
PROD001,BC001,1
PROD002,BC002,0
```

### 6. 准备数据（可选）

如果有自己的检测数据：

```bash
# 数据目录结构
data/
├── front/  # 正面图像 {id}-1.jpg
├── side/   # 侧面图像 {id}-3.jpg
└── back/   # 背面图像 {id}-2.jpg
```

### 7. 运行系统

```bash
python app.py
```

首次运行会显示启动画面，然后打开主界面。

## 故障排查

### 问题1：pyzbar 安装失败

**Windows**:
```bash
# 需要安装 Visual C++ 运行库
# 下载链接: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

**Linux**:
```bash
sudo apt-get install libzbar0
pip install pyzbar
```

**macOS**:
```bash
brew install zbar
pip install pyzbar
```

### 问题2：中文路径无法读取

系统已支持中文路径，使用 `imread_unicode()` 函数。确保：
- Python 环境编码为 UTF-8
- 文件名不包含特殊字符

### 问题3：CUDA 不可用

检查 CUDA 安装：
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

如果输出 `False`：
- 确认安装了正确版本的 PyTorch
- 检查 NVIDIA 驱动版本
- 重新安装 CUDA Toolkit

### 问题4：模型文件缺失

模型文件较大，未包含在仓库中。解决方案：

1. **使用训练脚本生成**：
   ```bash
   python train.py
   ```

2. **从备份下载**（如有）
3. **系统会自动使用配置模式**（基于标注文件）

## 开发环境配置

如果需要进行开发：

```bash
# 安装开发依赖
pip install flake8 black mypy pytest

# 安装 Git hooks
pre-commit install  # 如果使用 pre-commit
```

## Docker 部署（可选）

```bash
# 构建镜像
docker build -t jushen-detection .

# 运行容器
docker run -p 8000:8000 jushen-detection
```

## 卸载

```bash
# 删除虚拟环境
conda env remove -n jushen
# 或
rm -rf venv/

# 删除项目目录
cd ..
rm -rf JuShen-xiaci-detect/
```

## 下一步

- 阅读 [快速入门](quick-start.md) 运行 Demo
- 查看 [API 文档](api/) 了解接口
- 参考 [部署指南](../DEPLOYMENT.md) 用于生产环境

## 获取帮助

如遇问题：
- 查看 [常见问题](faq.md)
- 提交 [Issue](https://github.com/1984930808/JuShen-xiaci-detect/issues)
- 阅读 [故障排查文档](../DEPLOYMENT.md#故障排查)
