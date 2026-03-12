#!/usr/bin/env python3
"""测试音频属性移除功能"""
import os
import sys
import shutil
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.image_property_editor import add_media_property, remove_media_properties

def test_audio_property_removal():
    """测试音频属性移除功能"""
    print("开始测试音频属性移除功能...")
    
    # 复制测试音频文件到临时目录
    test_dir = tempfile.mkdtemp()
    ts_dir = os.path.join(os.path.dirname(__file__), "result", "ts")
    
    # 找到音频文件
    audio_files = []
    for file in os.listdir(ts_dir):
        if file.endswith('.mp3'):
            audio_files.append(file)
            break
    
    if not audio_files:
        print("没有找到测试音频文件")
        return
    
    test_file = audio_files[0]
    src_path = os.path.join(ts_dir, test_file)
    dst_path = os.path.join(test_dir, test_file)
    shutil.copy2(src_path, dst_path)
    
    print(f"测试文件: {dst_path}")
    
    try:
        # 1. 添加属性
        print("\n1. 添加属性...")
        add_result = add_media_property(dst_path, "Artist", "测试艺术家")
        print(f"添加属性结果: {add_result}")
        
        # 2. 移除属性
        print("\n2. 移除属性...")
        remove_result = remove_media_properties(dst_path, properties_to_remove=["Artist"])
        print(f"移除属性结果: {remove_result}")
        
        # 3. 测试移除所有属性
        print("\n3. 测试移除所有属性...")
        # 先重新添加属性
        add_media_property(dst_path, "Artist", "测试艺术家")
        add_media_property(dst_path, "Title", "测试标题")
        
        remove_all_result = remove_media_properties(dst_path, remove_all=True)
        print(f"移除所有属性结果: {remove_all_result}")
        
        print("\n测试完成！")
        
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir)
        print("\n临时目录已清理")

if __name__ == "__main__":
    test_audio_property_removal()
