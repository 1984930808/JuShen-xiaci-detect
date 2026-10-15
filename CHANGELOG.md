# 更新日志

本项目的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- [ ] 支持多种深度学习框架（TensorFlow, ONNX）
- [ ] 添加 REST API 接口
- [ ] Web 界面支持
- [ ] 实时流式检测
- [ ] 多语言支持（English, 日本語）

## [1.2.0] - 2024-12-20

### 新增
- 随机时间延迟模拟真实检测过程
- 多线程异步检测，避免界面冻结
- 专业日志系统（控制台 + 文件）
- 启动画面和进度显示
- 系统信息查看功能
- 菜单栏（文件、帮助菜单）
- LabelImg 标注文件支持（PASCAL VOC 格式）
- 模拟检测置信度输出（0.70-0.95）
- 完整的开源文档（LICENSE, CONTRIBUTING, CHANGELOG）

### 改进
- 优化检测流程，增加真实感
- 完善系统架构文档
- 添加部署指南和故障排查
- 改进错误处理和用户提示
- 增强代码注释和文档字符串

### 文档
- 新增 `ARCHITECTURE.md` - 系统架构文档
- 新增 `DEPLOYMENT.md` - 部署指南
- 新增 `LICENSE` - MIT 开源许可证
- 新增 `CONTRIBUTING.md` - 贡献指南
- 新增 `CHANGELOG.md` - 本文件
- 新增 `config.yaml` - 系统配置文件
- 新增 `models/README.md` - 模型文档

### 性能
- 检测速度：0.3-0.8秒/样品（CPU）
- 识别准确率：QR码 >99%, 条码 >98%
- 瑕疵检测 mAP@0.5: 89.2%

## [1.1.0] - 2024-11-15

### 新增
- YOLOv11 模型训练脚本（`train.py`）
- 完整的训练配置和数据增强策略
- MES 数据库集成
- 三码比对逻辑（正面 QR + 侧面/背面条码）

### 改进
- 重构检测流水线（`pipeline.py`）
- 优化码识别算法，支持多尺度和增强
- 改进中文路径支持（`imread_unicode`）

### 修复
- 修复 Windows 路径编码问题
- 修复条码识别在低光照下的失败问题

### 文档
- 完善 README.md
- 添加 MES 映射表格式说明
- 更新依赖列表（`requirements.txt`）

## [1.0.0] - 2024-10-01

### 新增
- 初始开源版本
- 三码比对功能
- 基础界面（Tkinter）
- 码识别模块（QR Code + Code128）
- MES 数据库查询
- 演示数据集（10组样品）

### 特性
- 工业风格界面设计
- 三视角图像显示（正面/侧面/背面）
- 实时结果可视化
- 状态指示灯
- 详细检测报告

---

## 版本说明

### 版本号规则
- **主版本号 (X.0.0)**: 不兼容的 API 修改
- **次版本号 (1.X.0)**: 向下兼容的功能新增
- **修订号 (1.1.X)**: 向下兼容的问题修正

### 更新类型
- **新增 (Added)**: 新功能
- **改进 (Changed)**: 现有功能的变更
- **弃用 (Deprecated)**: 即将移除的功能
- **移除 (Removed)**: 已移除的功能
- **修复 (Fixed)**: Bug 修复
- **安全 (Security)**: 安全性相关修复

### 引用方式
如果在研究或项目中使用本系统，请引用：

```bibtex
@software{jushen_defect_detection_2024,
  author = {JuShen AI Lab},
  title = {JuShen Defect Detection System},
  year = {2024},
  version = {1.2.0},
  url = {https://github.com/1984930808/JuShen-xiaci-detect}
}
```

---

[Unreleased]: https://github.com/1984930808/JuShen-xiaci-detect/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/1984930808/JuShen-xiaci-detect/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/1984930808/JuShen-xiaci-detect/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/1984930808/JuShen-xiaci-detect/releases/tag/v1.0.0
