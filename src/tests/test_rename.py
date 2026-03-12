#!/usr/bin/env python3
"""测试文件重命名功能"""
import os
import sys
import shutil
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.file_renamer import batch_rename_files

# 创建测试文件
def create_test_files(test_dir, count=5):
    """创建测试文件"""
    for i in range(1, count + 1):
        file_path = os.path.join(test_dir, f"测试文件 ({i}).txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"测试内容 {i}")
    print(f"创建了 {count} 个测试文件")

# 测试重命名
def test_rename():
    """测试重命名功能"""
    # 创建临时目录
    test_dir = tempfile.mkdtemp()
    print(f"测试目录: {test_dir}")
    
    try:
        # 创建测试文件
        create_test_files(test_dir)
        
        # 列出初始文件
        print("\n初始文件:")
        for file in os.listdir(test_dir):
            print(f"  - {file}")
        
        # 测试重命名
        print("\n开始重命名...")
        result = batch_rename_files(test_dir, "测试文件", start_value=1, digits=2, increment=1)
        
        # 显示结果
        print("\n重命名结果:")
        print(f"成功: {len(result.get('renamed', []))} 个文件")
        print(f"失败: {len(result.get('failed', []))} 个文件")
        
        # 列出重命名后的文件
        print("\n重命名后的文件:")
        for file in os.listdir(test_dir):
            print(f"  - {file}")
            
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir)
        print(f"\n清理测试目录: {test_dir}")

if __name__ == "__main__":
    test_rename()
