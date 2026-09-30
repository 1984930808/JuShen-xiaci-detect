# 巨神瑕疵检测 (jushenxiaci)

工业件 **三码比对 + 瑕疵检测** 开源演示项目。

当前已实现完整检测流程界面：正面二维码 → MES 查表 → 侧面/背面条码比对 → 假瑕疵检测（按 MES 标记演示）。真实视觉瑕疵模型可后续按同一接口替换。

## 功能流程

1. 扫描正面 `QR Code`，得到第一串 ID
2. 在 `MES-ID.cgf` 中查找对应第二串条码，以及瑕疵标记
3. 扫描侧面 / 背面 `Code128`，校验：侧面 == 背面 == MES 条码
4. 三码通过后进入瑕疵检测
   - 现阶段：第三列 `1` = 无瑕疵，`0` = 有瑕疵（可预留 `x:y` 坐标）
   - 后续：替换为真实检测模型

## 目录结构

```text
jushenxiaci/
├── app.py              # 检测界面入口
├── pipeline.py         # 三码比对 + 瑕疵检测流水线
├── mes_db.py           # MES-ID 文件读写
├── QRDecode.py         # 二维码 / 条码解码（支持中文路径读图）
├── MES-ID.cgf          # 演示用 MES 映射表
├── requirements.txt
└── data/
    ├── front/          # {id}-1.jpg  正面 QR
    ├── back/           # {id}-2.jpg  背面 Code128
    └── side/           # {id}-3.jpg  侧面 Code128
```

## MES 文件格式

```text
正面QR码,侧面背面条码,瑕疵标记[,x:y,...]
```

- 瑕疵标记：`1` 无瑕疵，`0` 有瑕疵
- 可选扩展列：`x:y` 瑕疵坐标，便于后续监督训练

示例：

```text
qjG8o3TPd1Z,9C0EA9EC,1
OqfSJH6wKG5,842ccafd,0,320:180
```

## 快速开始

```bash
# 建议使用独立环境（本仓库演示曾在 conda yolo_env 下运行）
pip install -r requirements.txt
python app.py
```

> Windows 下项目路径含中文时，请勿直接使用 `cv2.imread`；本项目已用 `imread_unicode` 处理。

### 推荐试跑样品

| 样品 | 预期 |
|------|------|
| 7 / 9 | 三码通过 + 无瑕疵 |
| 3 / 4 / 6 | 三码通过 + 有瑕疵（演示框） |
| 2 / 8 / 10 | 侧面 ≠ 背面，比对失败 |

## 真实瑕疵检测路线（建议）

按标注成熟度分阶段，不必一上来就上大模型：

### 阶段 A：只有 OK / NG（当前 MES 第三列）

优先用 **异常检测 / 无监督**，少瑕疵样本也能起步：

- 推荐：[Anomalib](https://github.com/openvinotoolkit/anomalib)（PatchCore / EfficientAD / PaDiM）
- 做法：只用良品图训练“正常分布”，推理时打异常热力图 + 分数阈值
- 适合：产线初期、瑕疵种类多、框标注还没到位

### 阶段 B：有瑕疵框 / 点坐标（MES 扩展 `x:y` 或 YOLO 标注）

走 **目标检测**，若已有 YOLO 环境，推荐直接接 **Ultralytics YOLO**：

1. 用 Labelme / Roboflow / CVAT 标缺陷框（可多类：划痕、凹陷、污渍…）
2. 导出 YOLO 格式，训练 `yolov8n/s` 或更新版本
3. 在 `pipeline._fake_defect_inspect` 位置替换为模型推理，输出 boxes 接到现有 UI

### 阶段 C：需要像素级轮廓

再用 **实例分割**（YOLO-seg / Mask R-CNN）。仅当质检要求面积、轮廓精确定量时再上，标注成本更高。

### 工程建议

- 先固定拍照位姿与曝光，比换更大模型更管用
- 三码比对继续作为硬门槛：比对失败不进入瑕疵模型
- 模型与 MES 解耦：MES 负责追溯 ID，模型负责视觉判定
- 保留假检测开关，方便无模型演示与 CI

## License

MIT
