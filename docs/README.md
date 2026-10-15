# 技术文档

本目录包含 JuShen 瑕疵检测系统的详细技术文档。

## 文档目录

### 快速开始
- [安装指南](installation.md) - 环境配置和依赖安装
- [快速入门](quick-start.md) - 5分钟上手指南
- [常见问题](faq.md) - 常见问题解答

### 核心功能
- [三码比对](code-matching.md) - QR码和条码识别原理
- [瑕疵检测](defect-detection.md) - YOLOv11 检测算法详解
- [MES 集成](mes-integration.md) - MES数据库集成方案

### API 文档
- [Pipeline API](api/pipeline.md) - 检测流水线接口
- [MES Database API](api/mes-db.md) - MES数据库接口
- [QR Decoder API](api/qr-decode.md) - 码识别接口

### 开发指南
- [代码结构](development/code-structure.md) - 项目代码组织
- [测试指南](development/testing.md) - 单元测试和集成测试
- [性能优化](development/performance.md) - 性能调优技巧

### 部署运维
- [Docker 部署](deployment/docker.md) - 容器化部署
- [生产环境配置](deployment/production.md) - 生产环境最佳实践
- [监控和日志](deployment/monitoring.md) - 系统监控方案

### 算法原理
- [目标检测原理](algorithms/object-detection.md) - YOLO 算法详解
- [图像增强](algorithms/image-enhancement.md) - 图像预处理技术
- [NMS 后处理](algorithms/nms.md) - 非极大值抑制算法

### 数据集
- [数据标注指南](dataset/labeling.md) - LabelImg 使用教程
- [数据集格式](dataset/format.md) - YOLO/PASCAL VOC 格式说明
- [数据增强策略](dataset/augmentation.md) - 训练数据增强

## 阅读建议

### 新用户
1. 阅读 [安装指南](installation.md)
2. 跟随 [快速入门](quick-start.md) 运行 Demo
3. 查看 [常见问题](faq.md) 解决疑问

### 开发者
1. 理解 [代码结构](development/code-structure.md)
2. 学习 [API 文档](api/)
3. 参考 [测试指南](development/testing.md) 编写测试

### 运维人员
1. 学习 [部署指南](deployment/)
2. 配置 [监控系统](deployment/monitoring.md)
3. 了解 [故障排查](faq.md#故障排查)

### 算法研究者
1. 深入 [算法原理](algorithms/)
2. 研究 [数据集处理](dataset/)
3. 参与 [性能优化](development/performance.md)

## 贡献文档

欢迎贡献文档！请遵循以下规范：

- 使用 Markdown 格式
- 添加目录和章节标题
- 提供代码示例
- 配图说明（如适用）
- 更新本 README 的文档目录

## 文档版本

- 当前版本：v1.2.0
- 最后更新：2024-12-20
- 维护者：JuShen AI Lab

## 反馈

如有文档问题或建议，请：
- 提交 [Issue](https://github.com/1984930808/JuShen-xiaci-detect/issues)
- 发送 Pull Request
- 联系维护团队
