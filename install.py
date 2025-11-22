#!/usr/bin/env python3
"""
天体系统模拟器安装脚本
自动安装必要的依赖包
"""

import sys
import subprocess
import importlib
import platform

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    """检查Python版本"""
    version = platform.python_version_tuple()
    major, minor = int(version[0]), int(version[1])
    
    if major < 3 or (major == 3 and minor < 7):
        print(f"❌ Python版本过低: {platform.python_version()}")
        print("需要Python 3.7或更高版本")
        return False
    
    print(f"✓ Python版本: {platform.python_version()}")
    return True

def main():
    """主安装函数"""
    print("天体系统模拟器安装程序")
    print("=" * 40)
    
    # 检查Python版本
    if not check_python_version():
        return 1
    
    # 核心依赖包
    core_packages = [
        "pygame>=2.1.0",
        "PyOpenGL>=3.1.5",
        "PyOpenGL-accelerate>=3.1.5",
        "numpy>=1.21.0",
        "Pillow>=8.3.0"
    ]
    
    # 可选依赖包
    optional_packages = [
        "numba>=0.56.0",
        "matplotlib>=3.4.0",
        "scipy>=1.7.0"
    ]
    
    print("\n正在安装核心依赖包...")
    print("-" * 30)
    
    success_count = 0
    total_count = len(core_packages)
    
    for package in core_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✓ {package} 安装成功")
            success_count += 1
        else:
            print(f"❌ {package} 安装失败")
    
    print(f"\n核心依赖包安装完成: {success_count}/{total_count}")
    
    if success_count < total_count:
        print("\n⚠️  部分核心包安装失败，程序可能无法正常运行")
        print("请手动安装失败的包")
        return 1
    
    print("\n正在安装可选依赖包...")
    print("-" * 30)
    
    optional_success = 0
    optional_total = len(optional_packages)
    
    for package in optional_packages:
        print(f"正在安装 {package}...")
        if install_package(package):
            print(f"✓ {package} 安装成功")
            optional_success += 1
        else:
            print(f"⚠️  {package} 安装失败（可选）")
    
    print(f"\n可选依赖包安装完成: {optional_success}/{optional_total}")
    
    # 检查CUDA支持
    print("\n正在检查CUDA支持...")
    try:
        subprocess.check_call([sys.executable, "-c", "import pycuda"])
        print("✓ PyCUDA已安装，可以使用CUDA加速")
    except:
        print("ℹ️  PyCUDA未安装，CUDA加速功能不可用")
        print("  如需CUDA加速，请手动安装: pip install pycuda")
    
    print("\n" + "=" * 40)
    print("安装完成！")
    print("\n现在可以运行模拟器:")
    print("  python run_simulator.py")
    print("\n或者运行测试:")
    print("  python test_simulator.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())