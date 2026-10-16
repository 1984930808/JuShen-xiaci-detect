#!/usr/bin/env python
"""验证安装脚本 - 检查环境和依赖。"""

import sys
from pathlib import Path


def check_python_version():
    """检查Python版本。"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("  ✅ Python版本符合要求 (>=3.8)")
        return True
    else:
        print("  ❌ Python版本过低，需要 >= 3.8")
        return False


def check_dependencies():
    """检查依赖包。"""
    required = {
        "opencv-python": "cv2",
        "numpy": "numpy",
        "Pillow": "PIL",
        "pyzbar": "pyzbar",
        "ultralytics": "ultralytics"
    }
    
    results = {}
    for package_name, import_name in required.items():
        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "unknown")
            print(f"  ✅ {package_name}: {version}")
            results[package_name] = True
        except ImportError:
            print(f"  ❌ {package_name}: 未安装")
            results[package_name] = False
    
    return all(results.values())


def check_files():
    """检查必需文件。"""
    required_files = [
        "MES-ID.cgf",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "app.py",
        "pipeline.py",
        "mes_db.py",
        "QRDecode.py"
    ]
    
    missing = []
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name}: 不存在")
            missing.append(file_name)
    
    return len(missing) == 0


def check_data():
    """检查演示数据。"""
    data_dirs = ["data/front", "data/side", "data/back"]
    
    all_exist = True
    for dir_name in data_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            # 统计文件数量
            jpg_count = len(list(dir_path.glob("*.jpg")))
            print(f"  ✅ {dir_name}: {jpg_count} 张图像")
        else:
            print(f"  ❌ {dir_name}: 目录不存在")
            all_exist = False
    
    return all_exist


def check_mes():
    """检查MES数据库。"""
    mes_path = Path("MES-ID.cgf")
    
    if not mes_path.exists():
        print("  ❌ MES-ID.cgf 文件不存在")
        return False
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from mes_db import MesDatabase
        mes = MesDatabase(mes_path)
        record_count = len(mes)
        print(f"  ✅ MES数据库: {record_count} 条记录")
        return True
    except Exception as e:
        print(f"  ❌ MES数据库加载失败: {e}")
        return False


def check_model():
    """检查模型文件。"""
    model_path = Path("models/best.pt")
    
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ 模型文件: {size_mb:.1f} MB")
        return True
    else:
        print("  ⚠️  模型文件不存在（将使用配置模式）")
        return True  # 不影响使用


def main():
    """运行所有检查。"""
    print("=" * 60)
    print("JuShen 瑕疵检测系统 - 安装验证")
    print("=" * 60)
    
    print("\n【1/6】检查Python版本")
    python_ok = check_python_version()
    
    print("\n【2/6】检查依赖包")
    deps_ok = check_dependencies()
    
    print("\n【3/6】检查必需文件")
    files_ok = check_files()
    
    print("\n【4/6】检查演示数据")
    data_ok = check_data()
    
    print("\n【5/6】检查MES数据库")
    mes_ok = check_mes()
    
    print("\n【6/6】检查模型文件")
    model_ok = check_model()
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    all_ok = python_ok and deps_ok and files_ok and data_ok and mes_ok
    
    if all_ok:
        print("\n✅ 所有检查通过！")
        print("\n下一步操作:")
        print("  1. 运行检测软件: python app.py")
        print("  2. 运行测试: python scripts/run_tests.py")
        print("  3. 查看文档: docs/installation.md")
        return 0
    else:
        print("\n❌ 部分检查未通过")
        print("\n解决方案:")
        
        if not python_ok:
            print("  • 升级Python到3.8+")
        
        if not deps_ok:
            print("  • 安装依赖: pip install -r requirements.txt")
        
        if not files_ok:
            print("  • 检查项目完整性，确认所有文件存在")
        
        if not data_ok:
            print("  • 检查data目录，确保演示数据存在")
        
        if not mes_ok:
            print("  • 检查MES-ID.cgf文件格式")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
