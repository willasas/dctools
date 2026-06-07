"""媒体属性编辑功能测试脚本"""
import os
from src.core.image_property_editor import batch_add_property, batch_remove_properties


def test_batch_add_properties():
    """测试批量添加属性"""
    folder_path = "E:\\AI玲珑\\ts"
    
    # 测试添加中文属性
    print("\n=== 测试添加中文属性 ===")
    print("添加 Artist 属性值为 '测试用户'")
    batch_add_property(folder_path, "Artist", "测试用户", recursive=True)
    
    print("\n添加 Title 属性值为 '测试标题'")
    batch_add_property(folder_path, "Title", "测试标题", recursive=True)
    
    print("\n添加 Copyright 属性值为 '测试版权'")
    batch_add_property(folder_path, "Copyright", "测试版权", recursive=True)
    
    # 测试添加英文属性
    print("\n=== 测试添加英文属性 ===")
    print("添加 Artist 属性值为 'Test User'")
    batch_add_property(folder_path, "Artist", "Test User", recursive=True)
    
    print("\n添加 Title 属性值为 'Test Title'")
    batch_add_property(folder_path, "Title", "Test Title", recursive=True)
    
    print("\n添加 Copyright 属性值为 'Test Copyright'")
    batch_add_property(folder_path, "Copyright", "Test Copyright", recursive=True)


def test_batch_remove_properties():
    """测试批量移除属性"""
    folder_path = "E:\\AI玲珑\\ts"
    
    print("\n=== 测试移除属性 ===")
    print("移除 Artist 属性")
    batch_remove_properties(folder_path, properties_to_remove=["Artist"], recursive=True)
    
    print("\n移除 Title 属性")
    batch_remove_properties(folder_path, properties_to_remove=["Title"], recursive=True)
    
    print("\n移除 Copyright 属性")
    batch_remove_properties(folder_path, properties_to_remove=["Copyright"], recursive=True)


if __name__ == "__main__":
    print("开始测试媒体属性编辑功能...")
    print(f"测试文件夹: E:\\AI玲珑\\ts")
    
    # 测试添加属性
    test_batch_add_properties()
    
    # 测试移除属性
    # test_batch_remove_properties()
    
    print("\n测试完成！")
