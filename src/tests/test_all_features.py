"""测试所有新增功能"""
import os
import sys
import shutil
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.core.file_renamer import (
    batch_rename_files, preview_rename, batch_rename_with_rules,
    preview_rename_with_rules, apply_rename_rules
)
from src.core.duplicate_remover import (
    remove_duplicates, preview_duplicates, get_duplicates_details
)
from src.core.excel_exporter import (
    export_to_excel, batch_export_folders
)
from src.core.folder_creator import (
    create_single_folder, batch_create_folders
)
from src.core.folder_info import (
    get_folder_info, get_all_files_info, export_to_txt, export_to_csv
)

print("\n===== 测试所有新增功能 =====\n")

# 创建临时测试目录
test_dir = tempfile.mkdtemp()
print(f"创建临时测试目录: {test_dir}")

# 测试数据
test_folders = ["测试文件夹1", "测试文件夹2", "测试文件夹3"]
test_files = ["test1.txt", "test2.txt", "test3.txt"]

try:
    # 1. 测试文件夹创建功能
    print("\n1. 测试文件夹创建功能")
    print("-" * 50)

    # 测试单个文件夹创建
    test_folder_path = create_single_folder("测试文件夹", test_dir)
    assert test_folder_path is not None, "单个文件夹创建失败"
    assert os.path.exists(test_folder_path), "创建的文件夹不存在"
    print("✅ 单个文件夹创建测试通过")

    # 测试批量文件夹创建
    folder_info_list = [{"name": folder_name, "path": test_dir} for folder_name in test_folders]
    created_folders = batch_create_folders(folder_info_list)
    assert len(created_folders) == len(test_folders), "批量文件夹创建失败"
    for folder_path in created_folders:
        assert os.path.exists(folder_path), f"创建的文件夹不存在: {folder_path}"
    print("✅ 批量文件夹创建测试通过")

    # 2. 创建测试文件
    print("\n2. 创建测试文件")
    print("-" * 50)

    test_file_paths = []
    for i, folder_path in enumerate(created_folders):
        for j, file_name in enumerate(test_files):
            file_path = os.path.join(folder_path, f"{i+1}_{file_name}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"测试内容 {i+1}-{j+1}")
            test_file_paths.append(file_path)

    # 创建重复文件用于测试去重
    duplicate_folder = os.path.join(test_dir, "重复文件测试")
    os.makedirs(duplicate_folder, exist_ok=True)

    # 创建原始文件
    original_file = os.path.join(duplicate_folder, "original.txt")
    with open(original_file, "w", encoding="utf-8") as f:
        f.write("这是原始文件内容")

    # 创建重复文件
    duplicate_file1 = os.path.join(duplicate_folder, "duplicate1.txt")
    duplicate_file2 = os.path.join(duplicate_folder, "duplicate2.txt")
    shutil.copy2(original_file, duplicate_file1)
    shutil.copy2(original_file, duplicate_file2)

    print(f"✅ 创建了 {len(test_file_paths)} 个测试文件")
    print(f"✅ 创建了 2 个重复测试文件")

    # 3. 测试文件重命名功能
    print("\n3. 测试文件重命名功能")
    print("-" * 50)

    # 选择一个测试文件夹进行重命名
    rename_test_folder = created_folders[0]

    # 测试预览重命名
    preview_result = preview_rename(rename_test_folder, "测试文件", start_value=1, digits=2, increment=1)
    assert len(preview_result) > 0, "预览重命名失败"
    print("✅ 预览重命名测试通过")

    # 测试批量重命名
    renamed_files = batch_rename_files(
        rename_test_folder, "测试文件", start_value=1, digits=2, increment=1
    )
    assert len(renamed_files) > 0, "批量重命名失败"
    print(f"✅ 批量重命名测试通过，重命名了 {len(renamed_files)} 个文件")

    # 测试重命名规则
    test_file_name = "test_file.txt"
    rules = [
        {"type": "prefix_suffix", "prefix": "prefix_", "suffix": "_suffix", "position": "before_ext"},
        {"type": "case", "case_type": "upper"}
    ]
    new_name = apply_rename_rules(test_file_name, rules)
    print(f"重命名规则测试: {test_file_name} -> {new_name}")
    # 修正预期结果，因为change_case函数只对文件名部分进行大小写转换
    assert "PREFIX" in new_name and "SUFFIX" in new_name and new_name.endswith(".txt"), "重命名规则应用失败"
    print("✅ 重命名规则测试通过")

    # 测试预览重命名规则
    preview_rules_result = preview_rename_with_rules(rename_test_folder, rules)
    assert len(preview_rules_result) > 0, "预览重命名规则失败"
    print("✅ 预览重命名规则测试通过")

    # 4. 测试Excel导出功能
    print("\n4. 测试Excel导出功能")
    print("-" * 50)

    # 使用未被重命名的文件夹中的文件进行测试
    test_files_folder = created_folders[1]  # 使用第二个文件夹，未被重命名

    # 获取该文件夹中的实际文件路径
    actual_files = []
    for file in os.listdir(test_files_folder):
        file_path = os.path.join(test_files_folder, file)
        if os.path.isfile(file_path):
            actual_files.append(file_path)

    # 测试单个文件导出
    if actual_files:
        excel_file = export_to_excel(actual_files[:3], "测试导出", test_dir)
        assert os.path.exists(excel_file), "Excel导出失败"
        assert os.path.getsize(excel_file) > 0, "导出的Excel文件为空"
        print("✅ 单个文件导出测试通过")
    else:
        print("⚠️  没有文件可用于Excel导出测试")

    # 测试批量文件夹导出
    if created_folders:
        batch_excel_file = batch_export_folders(created_folders[1:3], "批量导出", recursive=True)
        assert os.path.exists(batch_excel_file), "批量Excel导出失败"
        assert os.path.getsize(batch_excel_file) > 0, "批量导出的Excel文件为空"
        print("✅ 批量文件夹导出测试通过")
    else:
        print("⚠️  没有文件夹可用于批量Excel导出测试")

    # 5. 测试文件夹信息分析功能
    print("\n5. 测试文件夹信息分析功能")
    print("-" * 50)

    # 测试文件夹信息获取
    folder_info = get_folder_info(test_dir, recursive=True)
    assert folder_info is not None, "获取文件夹信息失败"
    assert folder_info["total_files"] > 0, "文件夹信息中文件数量为0"
    assert folder_info["total_folders"] > 0, "文件夹信息中文件夹数量为0"
    print("✅ 文件夹信息分析测试通过")

    # 测试文件详细信息获取
    files_info = get_all_files_info(test_dir, recursive=True)
    assert len(files_info) > 0, "获取文件详细信息失败"
    print("✅ 文件详细信息获取测试通过")

    # 测试导出为TXT
    txt_file = export_to_txt([test_dir], os.path.join(test_dir, "test_analysis.txt"), recursive=False)
    assert os.path.exists(txt_file), "导出TXT失败"
    assert os.path.getsize(txt_file) > 0, "导出的TXT文件为空"
    print("✅ 导出TXT测试通过")

    # 测试导出为CSV
    csv_file = export_to_csv([test_dir], os.path.join(test_dir, "test_analysis.csv"), recursive=False)
    assert os.path.exists(csv_file), "导出CSV失败"
    assert os.path.getsize(csv_file) > 0, "导出的CSV文件为空"
    print("✅ 导出CSV测试通过")

    # 6. 测试文件去重功能
    print("\n6. 测试文件去重功能")
    print("-" * 50)

    # 测试预览重复文件
    preview_count = preview_duplicates(duplicate_folder, method="hash", recursive=True)
    assert preview_count > 0, "预览重复文件失败"
    print("✅ 预览重复文件测试通过")

    # 测试获取重复文件详细信息
    duplicates_details = get_duplicates_details(duplicate_folder, method="hash", recursive=True)
    assert len(duplicates_details) > 0, "获取重复文件详细信息失败"
    print("✅ 获取重复文件详细信息测试通过")

    # 测试删除重复文件
    removed_count = remove_duplicates(duplicate_folder, method="hash", dry_run=False, recursive=True)
    assert removed_count > 0, "删除重复文件失败"
    print("✅ 删除重复文件测试通过")

    print("\n===== 所有功能测试通过！=====\n")

finally:
    # 清理测试目录
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"清理临时测试目录: {test_dir}")
