"""视频属性编辑功能测试脚本"""
import os
from src.core.image_property_editor import batch_add_property, batch_remove_properties


def test_video_properties():
    """测试视频属性编辑功能"""
    folder_path = "E:\\AI玲珑\\ts"
    
    # 测试添加视频属性
    print("=== 测试添加视频属性 ===")
    print("添加 Title 属性值为 '测试视频标题'")
    batch_add_property(folder_path, "Title", "测试视频标题", recursive=True)
    
    print("\n添加 Artist 属性值为 '测试视频作者'")
    batch_add_property(folder_path, "Artist", "测试视频作者", recursive=True)
    
    print("\n添加 Copyright 属性值为 '测试视频版权'")
    batch_add_property(folder_path, "Copyright", "测试视频版权", recursive=True)
    
    # 测试移除视频属性
    print("\n=== 测试移除视频属性 ===")
    print("移除 Title 属性")
    batch_remove_properties(folder_path, properties_to_remove=["Title"], recursive=True)
    
    print("\n移除 Artist 属性")
    batch_remove_properties(folder_path, properties_to_remove=["Artist"], recursive=True)
    
    print("\n移除 Copyright 属性")
    batch_remove_properties(folder_path, properties_to_remove=["Copyright"], recursive=True)


if __name__ == "__main__":
    print("开始测试视频属性编辑功能...")
    print(f"测试文件夹: E:\\AI玲珑\\ts")
    
    test_video_properties()
    
    print("\n测试完成！")
