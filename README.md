# JuShen 瑕疵检测 (JuShen-xiaci-detect)

面向工业产线的 **身份追溯 + 视觉瑕疵检测** 开源系统。

系统完成工件三码一致性校验后，对正面图像进行 YOLO 瑕疵目标检测，输出 OK / NG 判定与缺陷位置框，并与 MES 信息进行关联追溯。

仓库地址：https://github.com/1984930808/JuShen-xiaci-detect

## 系统能力

### 1. 三码比对（身份校验）

| 视角 | 码制 | 作用 |
|------|------|------|
| 正面 `front` | QR Code | 读取工件主 ID |
| 侧面 `side` | Code128 | 读取绑定条码 |
| 背面 `back` | Code128 | 读取绑定条码 |

流程：

1. 解码正面二维码，得到工件 ID  
2. 在 MES 映射表中查询期望条码与质检关联信息  
3. 解码侧面、背面条码，校验 **侧面 == 背面 == MES 条码**  
4. 仅当三码一致时，进入瑕疵视觉检测；否则直接判定身份校验失败

### 2. 瑕疵视觉检测

- 检测框架：Ultralytics **YOLOv11** 目标检测  
- 输入：三码通过后的正面图像（可扩展多视角）  
- 输出：缺陷类别、置信度、边界框坐标；无检出则为 OK  
- 结果可视化：在界面叠加缺陷框与 OK / NG 结论  
- 与 MES 联动：检测结果可回写/对照 MES 瑕疵标记，支持产线追溯
- **标注文件支持**：优先使用 LabelImg 标注文件（`.xml`），提供更精确的瑕疵框展示

### 3. 模型训练

提供 `train.py`，基于划分后的 YOLO 数据集进行训练与微调：

- 支持从预训练权重或已有 `best.pt` 继续训练  
- 输出目录：`runs/jushenzhineng/`  
- 训练完成后，将最佳权重接入检测流水线即可上线推理

## 目录结构

```text
JuShen-xiaci-detect/
├── app.py                 # 检测软件界面（选样 / 执行 / 结果展示）
├── pipeline.py            # 三码比对 + 瑕疵检测流水线
├── mes_db.py              # MES-ID 映射查询
├── QRDecode.py            # 二维码 / 条码解码（支持中文路径读图）
├── label_parser.py        # LabelImg 标注文件解析器（新增）
├── train.py               # YOLOv11 训练入口
├── MES-ID.cgf             # MES 映射表（QR → 条码 → 质检标记）
├── requirements.txt
├── 使用标注文件说明.md   # LabelImg 标注使用指南（新增）
├── data/                  # 演示采集图
│   ├── front/             # {id}-1.jpg  正面
│   │   └── annotations/   # {id}-1.xml  标注文件（可选）
│   ├── back/              # {id}-2.jpg  背面
│   └── side/              # {id}-3.jpg  侧面
├── yolo_dataset_split/    # YOLO 训练数据与 data.yaml（自备）
└── runs/                  # 训练输出与权重（自备，默认不入库）
```

## MES 映射表格式

```text
正面QR码,侧面背面条码,质检标记[,x:y,...]
```

| 字段 | 说明 |
|------|------|
| 正面 QR | 工件主身份 ID |
| 条码 | 侧面/背面应一致的 Code128 内容 |
| 质检标记 | `1` 良品，`0` 不良（可与视觉结果对照） |
| `x:y` | 可选缺陷点坐标，便于标注与复盘（仅在无 `.xml` 标注文件时使用） |

示例：

```text
qjG8o3TPd1Z,9C0EA9EC,1
OqfSJH6wKG5,842ccafd,0,320:180
```

## 瑕疵标注方式（二选一）

### 方式1：使用 LabelImg 标注文件（推荐）

使用 LabelImg 工具对正面图像进行精确标注，生成 PASCAL VOC 格式的 `.xml` 文件。

**优势**：
- ✅ 精确的瑕疵边界框
- ✅ 支持多个瑕疵
- ✅ 显示瑕疵类别名称
- ✅ 便于修改和调整

**使用方法**：参见 [使用标注文件说明.md](./使用标注文件说明.md)

```bash
# 安装 LabelImg
pip install labelimg

# 启动标注工具
labelimg data\front data\front\annotations
```

标注文件存放位置（任选其一）：
- `data/front/{id}-1.xml`（同目录）
- `data/front/annotations/{id}-1.xml`（推荐）
- `data/front/labels/{id}-1.xml`

### 方式2：使用 MES 配置坐标（快速）

在 `MES-ID.cgf` 第4列及以后添加 `x:y` 坐标点。

**示例**：
```text
OqfSJH6wKG5,842ccafd,0,320:180,450:200
```

**说明**：系统会在指定坐标周围生成固定大小的检测框。

**检测优先级**：标注文件（`.xml`）> MES 配置坐标

## 环境与运行

### 依赖安装

```bash
conda activate yolo_env   # 或自建虚拟环境
pip install -r requirements.txt
pip install ultralytics   # 训练 / YOLO 推理需要
```

### 启动检测软件

```bash
python app.py
```

1. 选择样品编号  
2. 点击「开始检测」  
3. 查看三码比对结果与瑕疵检测结论（含缺陷框）

> Windows 路径含中文时，请使用项目内 `imread_unicode` 读图，勿直接调用 `cv2.imread`。

### 训练瑕疵检测模型

1. 准备 YOLO 格式数据集，配置 `yolo_dataset_split/data.yaml`  
2. （可选）将已有权重放到 `runs/detect/yolo11_train3/weights/best.pt`  
3. 启动训练：

```bash
python train.py
```

训练参数（轮数、增强、损失权重等）可在 `train.py` 中按产线数据调整。训练完成后，将 `best.pt` 接入 `pipeline` 推理接口即可。

## 检测流水线说明

```text
正面图 / 侧面图 / 背面图
        │
        ▼
  码制解码（QR + Code128）
        │
        ▼
  MES 查表 → 期望条码
        │
        ▼
  三码一致性判定 ──失败──► 身份 NG，结束
        │通过
        ▼
  YOLO 瑕疵检测
        │
        ├── 无缺陷框 → 外观 OK
        └── 有缺陷框 → 外观 NG + 坐标/类别
```

## 演示数据说明

`data/` 提供多组三视角样例，可用于验证解码、比对与界面流程。部分样品侧面与背面故意不一致，用于验证身份校验拦截逻辑。

## License

MIT
