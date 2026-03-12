#!/usr/bin/env python3
"""处理文件：重命名、移动、复制和测试"""
import os
import sys
import shutil
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.file_renamer import batch_rename_files, batch_move_files
from src.core.duplicate_remover import remove_duplicates, preview_duplicates
from src.core.excel_exporter import export_to_excel
from src.core.image_property_editor import batch_add_property, batch_remove_properties
from src.core.folder_creator import create_single_folder

def get_result_dir():
    """获取结果目录"""
    result_dir = os.path.join(os.path.dirname(__file__), "result")
    os.makedirs(result_dir, exist_ok=True)
    return result_dir

def process_sheng_cai_er():
    """处理神印王座-圣采儿2文件夹"""
    print("\n===== 处理神印王座-圣采儿2文件夹 =====")
    result_dir = get_result_dir()
    source_folder = os.path.join(result_dir, "神印王座-圣采儿2")
    target_folder = os.path.join(result_dir, "S_圣采儿")
    
    # 创建目标文件夹
    create_single_folder("S_圣采儿", result_dir)
    
    # 重命名文件
    print("重命名文件...")
    rename_result = batch_rename_files(
        source_folder, "圣采儿", start_value=1, digits=3, increment=1,
        include_hidden=False, with_underscore=True, include_chinese=False
    )
    print(f"重命名成功: {len(rename_result['renamed'])} 个文件")
    print(f"重命名失败: {len(rename_result['failed'])} 个文件")
    
    # 移动文件
    print("\n移动文件...")
    files_to_move = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    move_result = batch_move_files(files_to_move, target_folder, overwrite=False)
    print(f"移动成功: {len(move_result['moved'])} 个文件")
    print(f"移动失败: {len(move_result['failed'])} 个文件")
    
    # 复制一些文件用于测试去重
    print("\n复制文件用于测试去重...")
    for i, file_name in enumerate(os.listdir(target_folder)[:3]):
        src = os.path.join(target_folder, file_name)
        dst = os.path.join(target_folder, f"copy_{i+1}_{file_name}")
        shutil.copy2(src, dst)
        print(f"复制: {file_name} -> copy_{i+1}_{file_name}")
    
    return target_folder

def process_heng_e():
    """处理师兄啊师兄-姮娥1文件夹"""
    print("\n===== 处理师兄啊师兄-姮娥1文件夹 =====")
    result_dir = get_result_dir()
    source_folder = os.path.join(result_dir, "师兄啊师兄-姮娥1")
    target_folder = os.path.join(result_dir, "H_姮娥")
    
    # 创建目标文件夹
    create_single_folder("H_姮娥", result_dir)
    
    # 重命名文件
    print("重命名文件...")
    rename_result = batch_rename_files(
        source_folder, "姮娥", start_value=1, digits=3, increment=1,
        include_hidden=False, with_underscore=True, include_chinese=False
    )
    print(f"重命名成功: {len(rename_result['renamed'])} 个文件")
    print(f"重命名失败: {len(rename_result['failed'])} 个文件")
    
    # 移动文件
    print("\n移动文件...")
    files_to_move = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    move_result = batch_move_files(files_to_move, target_folder, overwrite=False)
    print(f"移动成功: {len(move_result['moved'])} 个文件")
    print(f"移动失败: {len(move_result['failed'])} 个文件")
    
    # 复制一些文件用于测试去重
    print("\n复制文件用于测试去重...")
    for i, file_name in enumerate(os.listdir(target_folder)[:3]):
        src = os.path.join(target_folder, file_name)
        dst = os.path.join(target_folder, f"copy_{i+1}_{file_name}")
        shutil.copy2(src, dst)
        print(f"复制: {file_name} -> copy_{i+1}_{file_name}")
    
    return target_folder

def test_duplicate_removal():
    """测试去重功能"""
    print("\n===== 测试去重功能 =====")
    result_dir = get_result_dir()
    
    # 测试S_圣采儿文件夹
    print("测试S_圣采儿文件夹...")
    s_folder = os.path.join(result_dir, "S_圣采儿")
    if os.path.exists(s_folder):
        preview_count = preview_duplicates(s_folder, method="hash", recursive=True)
        print(f"预览重复文件: {preview_count} 个")
        removed_count = remove_duplicates(s_folder, method="hash", dry_run=False, recursive=True)
        print(f"删除重复文件: {removed_count} 个")
    
    # 测试H_姮娥文件夹
    print("\n测试H_姮娥文件夹...")
    h_folder = os.path.join(result_dir, "H_姮娥")
    if os.path.exists(h_folder):
        preview_count = preview_duplicates(h_folder, method="hash", recursive=True)
        print(f"预览重复文件: {preview_count} 个")
        removed_count = remove_duplicates(h_folder, method="hash", dry_run=False, recursive=True)
        print(f"删除重复文件: {removed_count} 个")

def test_excel_export():
    """测试Excel导出功能"""
    print("\n===== 测试Excel导出功能 =====")
    result_dir = get_result_dir()
    
    # 收集所有处理后的文件
    all_files = []
    
    # 添加S_圣采儿文件夹的文件
    s_folder = os.path.join(result_dir, "S_圣采儿")
    if os.path.exists(s_folder):
        for file in os.listdir(s_folder):
            file_path = os.path.join(s_folder, file)
            if os.path.isfile(file_path):
                all_files.append(file_path)
    
    # 添加H_姮娥文件夹的文件
    h_folder = os.path.join(result_dir, "H_姮娥")
    if os.path.exists(h_folder):
        for file in os.listdir(h_folder):
            file_path = os.path.join(h_folder, file)
            if os.path.isfile(file_path):
                all_files.append(file_path)
    
    # 导出Excel
    if all_files:
        print(f"导出 {len(all_files)} 个文件到Excel...")
        excel_file = export_to_excel(all_files, "处理后文件导出", result_dir)
        print(f"Excel导出成功: {excel_file}")
    else:
        print("没有文件可导出")

def test_media_properties():
    """测试媒体属性编辑功能"""
    print("\n===== 测试媒体属性编辑功能 =====")
    result_dir = get_result_dir()
    ts_folder = os.path.join(result_dir, "ts")
    
    if os.path.exists(ts_folder):
        # 测试添加属性
        print("添加媒体属性...")
        batch_add_property(ts_folder, "Artist", "测试艺术家", recursive=True)
        
        # 测试移除属性
        print("\n移除媒体属性...")
        batch_remove_properties(ts_folder, properties_to_remove=["Artist"], recursive=True)
    else:
        print("ts文件夹不存在")

def main():
    """主函数"""
    print("开始处理文件...")
    
    # 1. 处理神印王座-圣采儿2文件夹
    s_folder = process_sheng_cai_er()
    
    # 2. 处理师兄啊师兄-姮娥1文件夹
    h_folder = process_heng_e()
    
    # 3. 测试去重功能
    test_duplicate_removal()
    
    # 4. 测试Excel导出功能
    test_excel_export()
    
    # 5. 测试媒体属性编辑功能
    test_media_properties()
    
    print("\n所有处理和测试完成！")

if __name__ == "__main__":
    main()
