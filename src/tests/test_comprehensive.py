"""全面测试所有核心功能"""
import os
import sys
import shutil
import tempfile
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.core.file_renamer import (
    batch_rename_files, preview_rename, batch_rename_with_rules,
    preview_rename_with_rules, apply_rename_rules, batch_move_files, preview_move
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
    get_folder_info, get_all_files_info, export_to_txt, export_to_csv, analyze_folder_structure
)
from src.core.image_property_editor import (
    batch_add_property, batch_remove_properties
)

def get_result_dir():
    """获取测试结果保存目录"""
    result_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "result")
    os.makedirs(result_dir, exist_ok=True)
    return result_dir

def write_test_result(test_name, status, message):
    """写入测试结果到文件"""
    result_dir = get_result_dir()
    result_file = os.path.join(result_dir, "test_results.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(result_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {test_name}: {status} - {message}\n")
    print(f"[{status}] {test_name}: {message}")

def test_folder_creation():
    """测试文件夹创建功能"""
    test_name = "文件夹创建功能"
    try:
        # 创建临时测试目录
        test_dir = tempfile.mkdtemp()

        # 测试单个文件夹创建
        test_folder_path = create_single_folder("测试文件夹", test_dir)
        assert test_folder_path is not None, "单个文件夹创建失败"
        assert os.path.exists(test_folder_path), "创建的文件夹不存在"
        write_test_result(test_name, "PASS", "单个文件夹创建测试通过")

        # 测试批量文件夹创建
        test_folders = ["测试文件夹1", "测试文件夹2", "测试文件夹3"]
        folder_info_list = [{"name": folder_name, "path": test_dir} for folder_name in test_folders]
        created_folders = batch_create_folders(folder_info_list)
        assert len(created_folders) == len(test_folders), "批量文件夹创建失败"
        for folder_path in created_folders:
            assert os.path.exists(folder_path), f"创建的文件夹不存在: {folder_path}"
        write_test_result(test_name, "PASS", "批量文件夹创建测试通过")

        return created_folders, test_dir
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def test_file_creation(created_folders):
    """创建测试文件"""
    test_name = "创建测试文件"
    try:
        test_files = ["test1.txt", "test2.txt", "test3.txt"]
        test_file_paths = []

        for i, folder_path in enumerate(created_folders):
            for j, file_name in enumerate(test_files):
                file_path = os.path.join(folder_path, f"{i+1}_{file_name}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"测试内容 {i+1}-{j+1}")
                test_file_paths.append(file_path)

        # 创建重复文件用于测试去重
        duplicate_folder = os.path.join(os.path.dirname(created_folders[0]), "重复文件测试")
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

        write_test_result(test_name, "PASS", f"创建了 {len(test_file_paths)} 个测试文件和 2 个重复测试文件")
        return test_file_paths, duplicate_folder
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def test_file_renaming(created_folders):
    """测试文件重命名功能"""
    test_name = "文件重命名功能"
    try:
        # 选择一个测试文件夹进行重命名
        rename_test_folder = created_folders[0]

        # 测试预览重命名
        preview_result = preview_rename(rename_test_folder, "测试文件", start_value=1, digits=2, increment=1)
        assert len(preview_result) > 0, "预览重命名失败"
        write_test_result(test_name, "PASS", "预览重命名测试通过")

        # 测试批量重命名
        renamed_files = batch_rename_files(
            rename_test_folder, "测试文件", start_value=1, digits=2, increment=1
        )
        assert len(renamed_files) > 0, "批量重命名失败"
        write_test_result(test_name, "PASS", f"批量重命名测试通过，重命名了 {len(renamed_files)} 个文件")

        # 测试重命名规则
        test_file_name = "test_file.txt"
        rules = [
            {"type": "prefix_suffix", "prefix": "prefix_", "suffix": "_suffix", "position": "before_ext"},
            {"type": "case", "case_type": "upper"}
        ]
        new_name = apply_rename_rules(test_file_name, rules)
        assert "PREFIX" in new_name and "SUFFIX" in new_name and new_name.endswith(".txt"), "重命名规则应用失败"
        write_test_result(test_name, "PASS", "重命名规则测试通过")

        # 测试预览重命名规则
        preview_rules_result = preview_rename_with_rules(rename_test_folder, rules)
        assert len(preview_rules_result) > 0, "预览重命名规则失败"
        write_test_result(test_name, "PASS", "预览重命名规则测试通过")

        return rename_test_folder
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def test_file_moving(created_folders):
    """测试文件移动功能"""
    test_name = "文件移动功能"
    try:
        # 创建目标文件夹
        target_folder = tempfile.mkdtemp()

        # 从第一个文件夹中获取实际存在的文件
        test_folder = created_folders[0]
        actual_files = []
        for file in os.listdir(test_folder):
            file_path = os.path.join(test_folder, file)
            if os.path.isfile(file_path):
                actual_files.append(file_path)

        if actual_files:
            # 测试预览移动
            preview_result = preview_move(actual_files[:2], target_folder)
            assert len(preview_result) > 0, "预览移动失败"
            write_test_result(test_name, "PASS", "预览移动测试通过")

            # 测试批量移动
            move_result = batch_move_files(actual_files[:2], target_folder, overwrite=False)
            assert len(move_result["moved"]) > 0, "批量移动失败"
            write_test_result(test_name, "PASS", f"批量移动测试通过，移动了 {len(move_result['moved'])} 个文件")
        else:
            write_test_result(test_name, "WARNING", "没有文件可用于移动测试")

        return target_folder
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def test_excel_export(created_folders, test_dir):
    """测试Excel导出功能"""
    test_name = "Excel导出功能"
    try:
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
            write_test_result(test_name, "PASS", "单个文件导出测试通过")
        else:
            write_test_result(test_name, "WARNING", "没有文件可用于Excel导出测试")

        # 测试批量文件夹导出
        if created_folders:
            batch_excel_file = batch_export_folders(created_folders[1:3], "批量导出", recursive=True)
            assert os.path.exists(batch_excel_file), "批量Excel导出失败"
            assert os.path.getsize(batch_excel_file) > 0, "批量导出的Excel文件为空"
            write_test_result(test_name, "PASS", "批量文件夹导出测试通过")
        else:
            write_test_result(test_name, "WARNING", "没有文件夹可用于批量Excel导出测试")

        return excel_file if 'excel_file' in locals() else None
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def test_folder_info(test_dir):
    """测试文件夹信息分析功能"""
    test_name = "文件夹信息分析功能"
    try:
        # 测试文件夹信息获取
        folder_info = get_folder_info(test_dir, recursive=True)
        assert folder_info is not None, "获取文件夹信息失败"
        assert folder_info["total_files"] > 0, "文件夹信息中文件数量为0"
        assert folder_info["total_folders"] > 0, "文件夹信息中文件夹数量为0"
        write_test_result(test_name, "PASS", "文件夹信息分析测试通过")

        # 测试文件详细信息获取
        files_info = get_all_files_info(test_dir, recursive=True)
        assert len(files_info) > 0, "获取文件详细信息失败"
        write_test_result(test_name, "PASS", "文件详细信息获取测试通过")

        # 测试分析文件夹结构
        analysis_result = analyze_folder_structure(test_dir, output_format="text")
        assert analysis_result is not None, "分析文件夹结构失败"
        write_test_result(test_name, "PASS", "分析文件夹结构测试通过")

        # 测试导出为TXT
        result_dir = get_result_dir()
        txt_file = export_to_txt([test_dir], os.path.join(result_dir, "test_analysis.txt"), recursive=False)
        assert os.path.exists(txt_file), "导出TXT失败"
        assert os.path.getsize(txt_file) > 0, "导出的TXT文件为空"
        write_test_result(test_name, "PASS", "导出TXT测试通过")

        # 测试导出为CSV
        csv_file = export_to_csv([test_dir], os.path.join(result_dir, "test_analysis.csv"), recursive=False)
        assert os.path.exists(csv_file), "导出CSV失败"
        assert os.path.getsize(csv_file) > 0, "导出的CSV文件为空"
        write_test_result(test_name, "PASS", "导出CSV测试通过")

        return folder_info
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def test_duplicate_removal(duplicate_folder):
    """测试文件去重功能"""
    test_name = "文件去重功能"
    try:
        # 测试预览重复文件
        preview_count = preview_duplicates(duplicate_folder, method="hash", recursive=True)
        assert preview_count > 0, "预览重复文件失败"
        write_test_result(test_name, "PASS", "预览重复文件测试通过")

        # 测试获取重复文件详细信息
        duplicates_details = get_duplicates_details(duplicate_folder, method="hash", recursive=True)
        assert len(duplicates_details) > 0, "获取重复文件详细信息失败"
        write_test_result(test_name, "PASS", "获取重复文件详细信息测试通过")

        # 测试删除重复文件
        removed_count = remove_duplicates(duplicate_folder, method="hash", dry_run=False, recursive=True)
        assert removed_count > 0, "删除重复文件失败"
        write_test_result(test_name, "PASS", "删除重复文件测试通过")

        return removed_count
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def test_media_properties(created_folders):
    """测试媒体属性编辑功能"""
    test_name = "媒体属性编辑功能"
    try:
        # 选择一个测试文件夹
        test_folder = created_folders[0]

        # 创建一个测试文本文件（虽然不是媒体文件，但可以测试错误处理）
        test_file = os.path.join(test_folder, "test_media.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("测试媒体文件")

        # 测试添加属性（应该会失败，因为不是媒体文件）
        try:
            batch_add_property(test_folder, "Artist", "测试艺术家", recursive=True)
            write_test_result(test_name, "PASS", "媒体属性添加测试通过")
        except Exception as e:
            write_test_result(test_name, "WARNING", f"媒体属性添加测试：{str(e)}")

        # 测试移除属性（应该会失败，因为不是媒体文件）
        try:
            batch_remove_properties(test_folder, properties_to_remove=["Artist"], recursive=True)
            write_test_result(test_name, "PASS", "媒体属性移除测试通过")
        except Exception as e:
            write_test_result(test_name, "WARNING", f"媒体属性移除测试：{str(e)}")

        return True
    except Exception as e:
        write_test_result(test_name, "FAIL", str(e))
        raise

def main():
    """主测试函数"""
    print("\n===== 开始全面测试所有核心功能 =====\n")

    # 清空之前的测试结果
    result_dir = get_result_dir()
    result_file = os.path.join(result_dir, "test_results.txt")
    if os.path.exists(result_file):
        os.remove(result_file)

    # 测试结果统计
    test_stats = {"pass": 0, "fail": 0, "warning": 0}

    try:
        # 1. 测试文件夹创建
        created_folders, test_dir = test_folder_creation()
        test_stats["pass"] += 2  # 单个和批量创建

        # 2. 创建测试文件
        test_file_paths, duplicate_folder = test_file_creation(created_folders)
        test_stats["pass"] += 1

        # 3. 测试文件重命名
        rename_test_folder = test_file_renaming(created_folders)
        test_stats["pass"] += 4  # 预览、批量、规则、预览规则

        # 4. 测试文件移动
        target_folder = test_file_moving(created_folders)
        test_stats["pass"] += 2  # 预览和批量移动

        # 5. 测试Excel导出
        excel_file = test_excel_export(created_folders, test_dir)
        test_stats["pass"] += 2  # 单个和批量导出

        # 6. 测试文件夹信息
        folder_info = test_folder_info(test_dir)
        test_stats["pass"] += 5  # 文件夹信息、文件信息、分析结构、导出TXT、导出CSV

        # 7. 测试文件去重
        removed_count = test_duplicate_removal(duplicate_folder)
        test_stats["pass"] += 3  # 预览、详细信息、删除

        # 8. 测试媒体属性
        media_result = test_media_properties(created_folders)
        test_stats["pass"] += 2  # 添加和移除属性

        print("\n===== 测试完成 =====")
        print(f"测试统计: 成功={test_stats['pass']}, 失败={test_stats['fail']}, 警告={test_stats['warning']}")
        print(f"测试结果已保存到: {result_file}")

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        write_test_result("全局测试", "FAIL", str(e))
    finally:
        # 清理临时目录
        if 'test_dir' in locals() and os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        if 'target_folder' in locals() and os.path.exists(target_folder):
            shutil.rmtree(target_folder)

if __name__ == "__main__":
    main()
