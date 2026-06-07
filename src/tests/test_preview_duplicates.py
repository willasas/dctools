#!/usr/bin/env python3
"""测试重复文件预览功能"""
import os
import sys
import shutil
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.duplicate_remover import preview_duplicates

def test_preview_duplicates():
    """测试重复文件预览功能"""
    print("开始测试重复文件预览功能...")
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp()
    
    try:
        # 创建测试文件
        original_file = os.path.join(test_dir, "original.txt")
        with open(original_file, "w", encoding="utf-8") as f:
            f.write("这是原始文件内容")
        
        # 创建重复文件
        duplicate_file1 = os.path.join(test_dir, "duplicate1.txt")
        duplicate_file2 = os.path.join(test_dir, "duplicate2.txt")
        shutil.copy2(original_file, duplicate_file1)
        shutil.copy2(original_file, duplicate_file2)
        
        # 测试预览重复文件
        print("\n测试预览重复文件...")
        duplicate_count = preview_duplicates(test_dir, method="hash", recursive=True)
        print(f"\n预览结果: 发现 {duplicate_count} 个重复文件")
        
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir)
        print("\n测试完成，临时目录已清理")

if __name__ == "__main__":
    test_preview_duplicates()
