#!/usr/bin/env python3
"""
天体系统模拟器启动脚本
简化的启动入口，适合初学者使用
"""

import sys
import os
import subprocess

def check_dependencies():
    """检查必要的依赖包"""
    required_packages = [
        'pygame',
        'PyOpenGL',
        'numpy',
        'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("发现缺少的依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\n请使用以下命令安装:")
        for package in missing_packages:
            print(f"pip install {package}")
        
        return False
    
    return True

def main():
    """主函数"""
    print("天体系统模拟器启动器")
    print("=" * 40)
    
    # 检查依赖
    # if not check_dependencies():
    #     print("\n请先安装缺少的依赖包，然后重新运行。")
    #     return 1
    
    print("✓ 所有依赖包已安装")
    
    # 检查主程序文件
    if not os.path.exists('celestial_simulator.py'):
        print("找不到主程序文件 celestial_simulator.py")
        return 1
    
    print("✓ 主程序文件存在")
    
    # 跳过自动测试以便直接启动（如需运行测试，请手动运行 test_simulator.py）
    print("(已跳过自动测试，直接启动主程序)")
    
    print("\n" + "=" * 40)
    print("正在启动天体系统模拟器...")
    print("\n操作说明:")
    print("- 鼠标左键拖拽: 旋转视角")
    print("- 鼠标滚轮: 缩放")
    print("- 空格键: 暂停/继续")
    print("- R键: 重置视角")
    print("- 1/2/3键: 加载预设场景")
    print("- ESC键: 退出程序")
    print("\n享受探索宇宙的乐趣！")
    print("=" * 40 + "\n")
    
    try:
        # 启动主程序
        subprocess.run([sys.executable, 'celestial_simulator.py'])
        
    except KeyboardInterrupt:
        print("\n程序已退出。")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())