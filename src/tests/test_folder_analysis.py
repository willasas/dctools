"""测试文件夹分析功能"""
import os
from src.core.folder_info import get_all_files_info, export_to_txt, export_to_csv

print("\n===== 测试文件夹分析功能 =====\n")

# 测试当前目录
current_dir = os.getcwd()
print(f"测试目录: {current_dir}")

# 测试1: 获取文件详细信息
print("\n1. 测试获取文件详细信息...")
try:
    files_info = get_all_files_info(current_dir, recursive=False)
    print(f"✅ 获取到 {len(files_info)} 个文件信息")
    
    if files_info:
        print("\n文件信息示例:")
        for i, info in enumerate(files_info[:3]):  # 只显示前3个
            print(f"\n文件 {i+1}:")
            print(f"  名称: {info['file_name']}")
            print(f"  扩展名: {info['extension']}")
            print(f"  大小: {info['size_formatted']}")
            print(f"  路径: {info['full_path']}")
            print(f"  修改时间: {info['modification_time']}")
            print(f"  创建时间: {info['creation_time']}")
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")

# 测试2: 导出为TXT格式
print("\n2. 测试导出为TXT格式...")
try:
    txt_path = export_to_txt([current_dir], recursive=False)
    print(f"✅ TXT导出成功: {txt_path}")
    print(f"   文件大小: {os.path.getsize(txt_path)} 字节")
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")

# 测试3: 导出为CSV格式
print("\n3. 测试导出为CSV格式...")
try:
    csv_path = export_to_csv([current_dir], recursive=False)
    print(f"✅ CSV导出成功: {csv_path}")
    print(f"   文件大小: {os.path.getsize(csv_path)} 字节")
except Exception as e:
    print(f"❌ 测试失败: {str(e)}")

print("\n===== 测试完成 =====\n")
