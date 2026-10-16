#!/usr/bin/env python
"""运行测试脚本。"""

import sys
import subprocess
from pathlib import Path


def main():
    """运行所有测试。"""
    print("=" * 60)
    print("运行 JuShen 瑕疵检测系统测试")
    print("=" * 60)
    
    # 检查pytest是否安装
    try:
        import pytest
    except ImportError:
        print("❌ pytest 未安装")
        print("请运行: pip install -r requirements-dev.txt")
        sys.exit(1)
    
    # 运行测试
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=Path(__file__).parent.parent
    )
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 部分测试失败")
        print("=" * 60)
        
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
