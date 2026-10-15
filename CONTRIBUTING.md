# 贡献指南

感谢您对 JuShen 瑕疵检测系统的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议：

1. 检查 [Issues](https://github.com/1984930808/JuShen-xiaci-detect/issues) 确认问题未被报告
2. 创建新 Issue，使用清晰的标题和详细描述
3. 提供复现步骤、环境信息、截图或日志

**Issue 模板**：
```
### 问题描述
简要描述问题

### 复现步骤
1. 
2. 
3. 

### 期望行为
描述您期望的结果

### 实际行为
描述实际发生的情况

### 环境信息
- 操作系统：
- Python 版本：
- 依赖版本：opencv-python=xxx, ultralytics=xxx
```

### 提交代码

#### 准备工作

1. Fork 本仓库到您的账号
2. Clone 到本地：
   ```bash
   git clone https://github.com/YOUR-USERNAME/JuShen-xiaci-detect.git
   cd JuShen-xiaci-detect
   ```
3. 创建新分支：
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

#### 开发规范

**代码风格**：
- 遵循 PEP 8 规范
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 类型注解（推荐使用 Python 3.8+ 的类型提示）

**示例**：
```python
def detect_defects(image: np.ndarray, model_path: str) -> list[tuple[int, int, int, int]]:
    """
    检测图像中的瑕疵。
    
    Args:
        image: 输入图像（BGR格式）
        model_path: YOLO模型路径
        
    Returns:
        瑕疵边界框列表 [(x, y, w, h), ...]
    """
    # 实现代码
    pass
```

**提交信息**：
- 使用清晰的提交信息
- 遵循 Conventional Commits 规范
- 格式：`<type>(<scope>): <subject>`

类型（type）：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建或辅助工具变动

示例：
```bash
git commit -m "feat(detection): 添加多尺度检测支持"
git commit -m "fix(pipeline): 修复三码比对逻辑错误"
git commit -m "docs(readme): 更新安装说明"
```

#### 测试要求

提交代码前，请确保：

1. **通过现有测试**：
   ```bash
   python -m pytest tests/
   ```

2. **添加新测试**（如适用）：
   - 单元测试：针对单个函数/类
   - 集成测试：验证模块间交互
   - 测试文件命名：`test_*.py`

3. **代码检查**：
   ```bash
   # 安装检查工具
   pip install flake8 black mypy
   
   # 运行检查
   flake8 *.py
   black --check *.py
   mypy *.py
   ```

#### 提交 Pull Request

1. 推送到您的 fork：
   ```bash
   git push origin feature/your-feature-name
   ```

2. 在 GitHub 上创建 Pull Request
3. 填写 PR 模板：
   - 描述改动内容
   - 关联相关 Issue（如 `Fixes #123`）
   - 列出测试步骤

**PR 模板**：
```
### 改动说明
简要描述本次改动

### 改动类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化
- [ ] 其他

### 相关 Issue
关联 Issue #xxx

### 测试
描述如何测试本次改动

### Checklist
- [ ] 代码遵循项目规范
- [ ] 已添加/更新测试
- [ ] 已更新文档
- [ ] 所有测试通过
- [ ] Commit 信息清晰
```

4. 等待代码审查
5. 根据反馈修改（如需要）

## 开发环境设置

### 依赖安装

```bash
# 创建虚拟环境
conda create -n jushen python=3.10
conda activate jushen

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt  # 如果有
```

### 项目结构

```
JuShen-xiaci-detect/
├── app.py              # 主界面
├── pipeline.py         # 检测流水线
├── mes_db.py          # MES 数据库
├── QRDecode.py        # 码识别
├── label_parser.py    # 标注解析
├── train.py           # 模型训练
├── tests/             # 测试文件
├── docs/              # 文档
└── models/            # 模型文件
```

## 功能开发建议

### 优先级领域

1. **检测精度提升**
   - 小目标检测优化
   - 新瑕疵类别支持
   - 数据增强策略

2. **性能优化**
   - 推理速度提升
   - 内存使用优化
   - 批量处理支持

3. **功能扩展**
   - 多视角融合
   - 在线学习
   - 结果统计分析

4. **工程化改进**
   - 容器化部署
   - REST API 接口
   - 配置管理优化

### 不接受的贡献

- 破坏性改动（未经讨论）
- 未经测试的代码
- 不符合项目目标的功能
- 代码质量低下或风格不一致

## 代码审查流程

1. **自动检查**：CI/CD 自动运行测试和代码检查
2. **人工审查**：至少一位维护者审查代码
3. **反馈修改**：根据审查意见修改代码
4. **合并**：审查通过后合并到主分支

## 版本发布

遵循语义化版本（Semantic Versioning）：
- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能新增
- **修订号**：向下兼容的问题修正

## 社区行为准则

### 我们的承诺

为建设开放友好的环境，我们承诺：
- 尊重不同观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他成员表现出同理心

### 不可接受的行为

- 使用性暗示的言语或图像
- 人身攻击、侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人私人信息
- 其他不道德或不专业的行为

## 联系方式

- **Issue**: https://github.com/1984930808/JuShen-xiaci-detect/issues
- **邮件**: [可选]
- **微信群**: [可选]

## 许可证

通过向本项目贡献代码，您同意您的贡献将在 [MIT License](LICENSE) 下授权。

---

再次感谢您的贡献！ 🎉
