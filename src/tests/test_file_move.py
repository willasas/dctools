"""测试文件批量移动功能"""
import os
import sys
import shutil
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.core.file_renamer import batch_move_files, preview_move, batch_rename_files

print("\n===== 测试文件批量移动功能 =====\n")

# 创建临时测试目录
test_dir = tempfile.mkdtemp()
target_dir = os.path.join(test_dir, "目标文件夹")
print(f"创建临时测试目录: {test_dir}")
print(f"创建目标文件夹: {target_dir}")

# 测试数据
test_files = ["test1.txt", "test2.txt", "test3.txt"]
test_file_paths = []

try:
    # 创建测试文件
    print("\n1. 创建测试文件")
    print("-" * 50)

    for file_name in test_files:
        file_path = os.path.join(test_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"测试内容: {file_name}")
        test_file_paths.append(file_path)
        print(f"✅ 创建文件: {file_path}")

    # 2. 测试预览移动功能
    print("\n2. 测试预览移动功能")
    print("-" * 50)

    preview_result = preview_move(test_file_paths, target_dir)
    assert len(preview_result) == len(test_file_paths), "预览移动结果数量不正确"
    print("✅ 预览移动功能测试通过")

    # 3. 测试批量移动功能
    print("\n3. 测试批量移动功能")
    print("-" * 50)

    move_result = batch_move_files(test_file_paths, target_dir)
    assert len(move_result["moved"]) == len(test_file_paths), "移动成功的文件数量不正确"
    assert len(move_result["failed"]) == 0, "移动失败的文件数量不为0"
    print("✅ 批量移动功能测试通过")

    # 验证文件是否移动成功
    print("\n4. 验证文件移动结果")
    print("-" * 50)

    for file_name in test_files:
        # 检查原位置文件是否不存在
        original_path = os.path.join(test_dir, file_name)
        assert not os.path.exists(original_path), f"原文件仍存在: {original_path}"

        # 检查目标位置文件是否存在
        target_path = os.path.join(target_dir, file_name)
        assert os.path.exists(target_path), f"目标文件不存在: {target_path}"
        print(f"✅ 验证成功: {file_name} 已移动到目标文件夹")

    # 5. 测试重命名后移动功能
    print("\n5. 测试重命名后移动功能")
    print("-" * 50)

    # 在目标文件夹中创建新的测试文件用于重命名
    rename_test_files = []
    for i in range(3):
        file_name = f"rename_test{i+1}.txt"
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"重命名测试内容: {file_name}")
        rename_test_files.append(file_path)

    # 重命名文件
    renamed_files = batch_rename_files(target_dir, "测试文件", start_value=1, digits=2)
    assert len(renamed_files) > 0, "重命名失败"
    print(f"✅ 重命名成功，重命名了 {len(renamed_files)} 个文件")

    # 创建新的目标文件夹用于移动重命名后的文件
    renamed_target_dir = os.path.join(test_dir, "重命名后目标文件夹")

    # 移动重命名后的文件
    move_renamed_result = batch_move_files(renamed_files, renamed_target_dir)
    assert len(move_renamed_result["moved"]) == len(renamed_files), "移动重命名后文件失败"
    print(f"✅ 移动重命名后文件成功，移动了 {len(move_renamed_result['moved'])} 个文件")

    # 验证重命名后的文件是否移动成功
    for file_path in renamed_files:
        # 检查原位置文件是否不存在
        assert not os.path.exists(file_path), f"重命名后原文件仍存在: {file_path}"

        # 检查目标位置文件是否存在
        file_name = os.path.basename(file_path)
        target_path = os.path.join(renamed_target_dir, file_name)
        assert os.path.exists(target_path), f"重命名后目标文件不存在: {target_path}"
    print("✅ 重命名后文件移动验证成功")

    # 6. 测试覆盖模式
    print("\n6. 测试覆盖模式")
    print("-" * 50)

    # 在目标文件夹中创建同名文件
    for file_name in test_files:
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"原始内容: {file_name}")

    # 重新创建测试文件
    new_test_file_paths = []
    for file_name in test_files:
        file_path = os.path.join(test_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"新内容: {file_name}")
        new_test_file_paths.append(file_path)

    # 测试覆盖模式移动
    overwrite_result = batch_move_files(new_test_file_paths, target_dir, overwrite=True)
    assert len(overwrite_result["moved"]) == len(new_test_file_paths), "覆盖模式移动失败"
    print("✅ 覆盖模式移动测试通过")

    # 验证文件内容是否被覆盖
    for file_name in test_files:
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "新内容" in content, f"文件内容未被覆盖: {file_name}"
    print("✅ 覆盖模式内容验证成功")

    print("\n===== 所有文件移动功能测试通过！=====\n")

finally:
    # 清理测试目录
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"清理临时测试目录: {test_dir}")
