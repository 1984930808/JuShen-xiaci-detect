# 部署指南

## 系统要求

### 硬件要求

- CPU: Intel i5 或以上
- 内存: 8GB RAM (推荐 16GB)
- GPU: NVIDIA GPU (支持 CUDA 11.0+) - 可选，用于加速推理
- 存储: 至少 10GB 可用空间

### 软件要求

- 操作系统: Windows 10/11 或 Linux (Ubuntu 20.04+)
- Python: 3.8 - 3.11
- CUDA: 11.0+ (如使用GPU)
- Git: 用于版本管理

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd JuShen-xiaci-detect
```

### 2. 创建虚拟环境

```bash
# 使用 conda (推荐)
conda create -n yolo_env python=3.10
conda activate yolo_env

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Linux
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 获取模型文件

模型文件由于体积较大，未包含在代码仓库中。请通过以下方式获取：

**方式1：从内部服务器复制**
```bash
# Windows
copy \\server\models\jushen\best.pt models\best.pt

# Linux
scp user@server:/models/jushen/best.pt models/best.pt
```

**方式2：从训练输出复制**
```bash
# 如果您已完成训练
copy runs\jushenzhineng\zhineng_train\weights\best.pt models\best.pt
```

**方式3：使用预训练模型（首次部署）**
```bash
# 系统会在首次运行时提示下载
python app.py
```

### 5. 配置 MES 数据库

编辑 `MES-ID.cgf` 文件，添加您的产品映射关系：

```
正面QR码,条码,质检标记
PROD001,BC001,1
PROD002,BC002,0
```

格式说明：
- 第1列：正面二维码内容
- 第2列：侧面/背面条码内容
- 第3列：质检标记 (1=合格, 0=不合格)

### 6. 运行系统

```bash
python app.py
```

## 验证安装

运行以下命令验证安装：

```bash
python -c "import cv2, numpy, pyzbar; print('✓ 依赖库正常')"
python -c "from pipeline import InspectionPipeline; print('✓ 流水线模块正常')"
```

## 生产环境配置

### 性能优化

1. **使用 GPU 推理**
   ```python
   # pipeline.py 中配置 GPU
   device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
   ```

2. **批量处理**
   - 适用于离线检测场景
   - 可显著提升吞吐量

3. **模型量化** (可选)
   ```bash
   # 将模型转换为 ONNX 格式加速
   python -m ultralytics.export model=models/best.pt format=onnx
   ```

### 日志配置

创建 `logging.conf` 配置文件：

```ini
[loggers]
keys=root,pipeline

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_pipeline]
level=DEBUG
handlers=fileHandler
qualname=pipeline
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=detailedFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=detailedFormatter
args=('inspection.log', 'a')

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 数据备份

定期备份以下文件：
- `MES-ID.cgf` - MES映射表
- `data/` - 检测图像
- `models/` - 模型文件
- `inspection.log` - 检测日志

## 故障排查

### 常见问题

**1. 无法识别二维码/条码**
- 检查图像质量和光照条件
- 确认 pyzbar 正确安装：`pip install pyzbar`
- Windows 需要安装 Visual C++ 运行库

**2. 模型加载失败**
- 确认 `models/best.pt` 存在
- 检查文件完整性（大小应为 ~6MB）
- 确认 ultralytics 版本：`pip install ultralytics>=8.3.0`

**3. 中文路径问题**
- 系统已支持中文路径
- 使用 `imread_unicode()` 而非 `cv2.imread()`

**4. GPU 不可用**
- 安装 CUDA 和 cuDNN
- 确认 PyTorch 支持 GPU：`python -c "import torch; print(torch.cuda.is_available())"`

### 日志分析

检查日志文件 `inspection.log`：

```bash
# 查看最近的错误
grep "ERROR" inspection.log | tail -20

# 统计检测结果
grep "检测到" inspection.log | wc -l
```

## 维护建议

1. **定期更新模型**: 根据新数据重新训练
2. **监控检测准确率**: 记录并分析误检和漏检
3. **备份重要数据**: 每周备份一次
4. **版本控制**: 使用 Git 管理代码变更

## 技术支持

如遇到问题，请联系技术团队或查阅：
- 项目文档: `README.md`
- 训练指南: `train.py` 注释
- GitHub Issues: <repository-url>/issues
