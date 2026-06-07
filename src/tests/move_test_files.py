#!/usr/bin/env python3
"""移动测试文件到tests文件夹"""
import os
import shutil

# 定义源文件和目标文件夹
source_files = [
    "test_preview_gui.py",
    "test_all_features.py"
]
target_folder = "src/tests"

# 确保目标文件夹存在
os.makedirs(target_folder, exist_ok=True)

# 移动文件
for file in source_files:
    if os.path.exists(file):
        target_path = os.path.join(target_folder, os.path.basename(file))
        shutil.move(file, target_path)
        print(f"移动文件: {file} -> {target_path}")
    else:
        print(f"文件不存在: {file}")

print("移动完成！")
