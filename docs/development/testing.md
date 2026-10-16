# 测试指南

本文档介绍如何编写和运行测试。

## 测试框架

项目使用 **pytest** 作为测试框架。

### 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

## 运行测试

### 运行所有测试

```bash
# 使用测试脚本
python scripts/run_tests.py

# 或直接使用pytest
pytest tests/ -v
```

### 运行特定测试文件

```bash
# 测试MES数据库
pytest tests/test_mes_db.py -v

# 测试QR解码
pytest tests/test_qr_decode.py -v

# 测试流水线
pytest tests/test_pipeline.py -v
```

### 运行特定测试用例

```bash
# 运行单个测试函数
pytest tests/test_pipeline.py::TestInspectionPipeline::test_sample_2_detection -v

# 运行单个测试类
pytest tests/test_pipeline.py::TestCodeMatching -v
```

### 带覆盖率报告

```bash
# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 查看报告
# Windows
start htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html
```

## 测试结构

```
tests/
├── __init__.py
├── test_mes_db.py      # MES数据库测试
├── test_qr_decode.py   # QR码/条码解码测试
└── test_pipeline.py    # 检测流水线测试
```

## 编写测试

### 基础测试

```python
import pytest
from mes_db import MESDatabase


def test_mes_loading():
    """测试MES数据加载。"""
    mes = MESDatabase("MES-ID.cgf")
    assert len(mes.records) > 0, "MES记录不应为空"
```

### 使用Fixture

```python
import pytest
from pathlib import Path
from pipeline import InspectionPipeline


@pytest.fixture
def pipeline():
    """创建检测流水线实例。"""
    ROOT = Path(__file__).parent.parent
    MES_PATH = ROOT / "MES-ID.cgf"
    MODEL_PATH = ROOT / "models" / "best.pt"
    return InspectionPipeline(MES_PATH, MODEL_PATH)


def test_sample_2_detection(pipeline):
    """测试样品2的检测。"""
    ROOT = Path(__file__).parent.parent
    DATA_ROOT = ROOT / "data"
    
    result = pipeline.inspect_sample_dir(DATA_ROOT, "2")
    
    assert result is not None
    assert result.sample_id == "2"
```

### 参数化测试

```python
import pytest
from pathlib import Path
from pipeline import InspectionPipeline, StepStatus


@pytest.fixture
def pipeline():
    ROOT = Path(__file__).parent.parent
    return InspectionPipeline(ROOT / "MES-ID.cgf", ROOT / "models" / "best.pt")


@pytest.mark.parametrize("sample_id,expected_overall", [
    ("2", StepStatus.PASS),  # 样品2应该通过
    ("3", StepStatus.FAIL),  # 样品3应该失败（有瑕疵）
    ("6", StepStatus.FAIL),  # 样品6应该失败（有瑕疵）
])
def test_sample_detection(pipeline, sample_id, expected_overall):
    """测试多个样品的检测结果。"""
    ROOT = Path(__file__).parent.parent
    result = pipeline.inspect_sample_dir(ROOT / "data", sample_id)
    
    assert result.overall == expected_overall
```

### 跳过测试

```python
import pytest


@pytest.mark.skip(reason="需要真实模型文件")
def test_yolo_inference():
    """测试YOLO推理（需要模型文件）。"""
    # 这个测试会被跳过
    pass


@pytest.mark.skipif(
    not Path("models/best.pt").exists(),
    reason="模型文件不存在"
)
def test_model_detection():
    """测试模型检测（仅在模型存在时运行）。"""
    # 仅在模型文件存在时运行
    pass
```

### 异常测试

```python
import pytest
from mes_db import MESDatabase


def test_invalid_mes_file():
    """测试无效MES文件。"""
    with pytest.raises(FileNotFoundError):
        MESDatabase("nonexistent.cgf")


def test_invalid_sample_id():
    """测试无效样品ID。"""
    from pipeline import InspectionPipeline
    from pathlib import Path
    
    ROOT = Path(__file__).parent.parent
    pipeline = InspectionPipeline(ROOT / "MES-ID.cgf", None)
    
    # 不应该崩溃
    result = pipeline.inspect_sample_dir(ROOT / "data", "invalid_id")
    # 结果可能是None或失败状态
```

### 性能测试

```python
import pytest
import time
from pathlib import Path
from pipeline import InspectionPipeline


@pytest.mark.slow
def test_detection_speed():
    """测试检测速度。"""
    ROOT = Path(__file__).parent.parent
    pipeline = InspectionPipeline(ROOT / "MES-ID.cgf", ROOT / "models" / "best.pt")
    
    start = time.time()
    result = pipeline.inspect_sample_dir(ROOT / "data", "2")
    elapsed = time.time() - start
    
    # CPU模式下应该在5秒内完成
    assert elapsed < 5.0, f"检测耗时过长: {elapsed:.2f}秒"
```

## 测试标记

项目使用pytest标记分类测试：

```python
import pytest


@pytest.mark.slow
def test_slow_operation():
    """慢速测试。"""
    pass


@pytest.mark.integration
def test_integration():
    """集成测试。"""
    pass
```

运行特定标记的测试：

```bash
# 运行慢速测试
pytest tests/ -m slow

# 排除慢速测试
pytest tests/ -m "not slow"

# 运行集成测试
pytest tests/ -m integration
```

## 测试覆盖率

### 生成覆盖率报告

```bash
# 终端输出
pytest tests/ --cov=. --cov-report=term

# HTML报告
pytest tests/ --cov=. --cov-report=html

# 同时生成两种报告
pytest tests/ --cov=. --cov-report=term --cov-report=html
```

### 覆盖率目标

- **总体覆盖率**: ≥ 70%
- **核心模块**: ≥ 80%
  - `pipeline.py`
  - `mes_db.py`
  - `QRDecode.py`

### 查看覆盖率详情

```bash
# 生成报告
pytest tests/ --cov=. --cov-report=html

# 查看报告
# Windows
start htmlcov/index.html

# 浏览器中查看详细覆盖情况
```

## 持续集成

项目使用GitHub Actions进行持续集成测试。

### 配置文件

`.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 测试最佳实践

### 1. 测试命名

```python
# ✅ 好的命名
def test_mes_query_by_qr_code():
    pass

# ❌ 不好的命名
def test_mes():
    pass
```

### 2. 测试隔离

```python
# ✅ 每个测试独立
def test_sample_2():
    pipeline = InspectionPipeline("MES-ID.cgf", None)
    result = pipeline.inspect_sample_dir("data", "2")
    assert result.sample_id == "2"

def test_sample_3():
    pipeline = InspectionPipeline("MES-ID.cgf", None)
    result = pipeline.inspect_sample_dir("data", "3")
    assert result.sample_id == "3"
```

### 3. 使用Fixture共享资源

```python
# ✅ 使用Fixture
@pytest.fixture
def pipeline():
    return InspectionPipeline("MES-ID.cgf", None)

def test_sample_2(pipeline):
    result = pipeline.inspect_sample_dir("data", "2")
    assert result.sample_id == "2"

def test_sample_3(pipeline):
    result = pipeline.inspect_sample_dir("data", "3")
    assert result.sample_id == "3"
```

### 4. 断言明确

```python
# ✅ 明确的断言消息
assert result.overall == StepStatus.PASS, f"样品2应该通过，实际: {result.overall}"

# ❌ 没有消息
assert result.overall == StepStatus.PASS
```

### 5. 测试边界条件

```python
def test_empty_qr_code():
    """测试空QR码。"""
    mes = MESDatabase("MES-ID.cgf")
    result = mes.query_by_qr("")
    assert result is None

def test_invalid_barcode():
    """测试无效条码。"""
    mes = MESDatabase("MES-ID.cgf")
    result = mes.query_by_barcode("INVALID_BARCODE")
    assert result is None
```

## 调试测试

### 详细输出

```bash
# 显示print输出
pytest tests/ -v -s

# 显示详细的断言信息
pytest tests/ -v --tb=long
```

### 进入调试器

```bash
# 在失败时进入pdb
pytest tests/ --pdb

# 在开始时进入pdb
pytest tests/ --trace
```

### 只运行失败的测试

```bash
# 第一次运行
pytest tests/ -v

# 只运行上次失败的测试
pytest tests/ --lf

# 先运行失败的，再运行其他的
pytest tests/ --ff
```

## 参考资源

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)
