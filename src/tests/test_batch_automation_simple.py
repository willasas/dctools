#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量自动化功能简单测试
"""
import os
import json
import shutil
import tempfile
import unittest
from src.core.duplicate_remover import remove_duplicates, preview_duplicates
from src.core.file_renamer import batch_rename_files

class TestBatchAutomationSimple(unittest.TestCase):
    """批量自动化功能简单测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, "source")
        self.target_dir = os.path.join(self.temp_dir, "target")

        # 创建源目录和测试文件
        os.makedirs(self.source_dir)

        # 创建测试子目录
        self.test_subdir = os.path.join(self.source_dir, "陆雪琪")
        os.makedirs(self.test_subdir)

        # 创建测试文件
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_subdir, f"test_file_{i}.png")
            with open(file_path, "w") as f:
                f.write(f"test content {i}")
            self.test_files.append(file_path)

        # 创建重复文件
        self.duplicate_file = os.path.join(self.test_subdir, "test_file_duplicate.png")
        shutil.copy2(self.test_files[0], self.duplicate_file)

        # 模拟文件夹映射
        self.folder_mapping = {
            "陆雪琪": "L_陆雪琪"
        }

    def tearDown(self):
        """清理测试环境"""
        # 删除临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_duplicate_removal(self):
        """测试去重功能"""
        # 预览重复文件
        duplicate_count, preview_details = preview_duplicates(self.test_subdir, method="hash", recursive=False)
        self.assertEqual(duplicate_count, 1)

        # 去重
        remove_duplicates(self.test_subdir, method="hash", recursive=False)

        # 检查重复文件是否被删除
        files = os.listdir(self.test_subdir)
        self.assertEqual(len(files), 3)

    def test_batch_rename(self):
        """测试批量重命名功能"""
        # 先去重
        remove_duplicates(self.test_subdir, method="hash", recursive=False)

        # 重命名文件
        result = batch_rename_files(
            self.test_subdir,
            "陆雪琪",
            naming_rule="{type}_{pinyin_name}_{timestamp}_{index}",
            start_value=1,
            digits=5,
            increment=1
        )

        # 检查重命名是否成功
        self.assertTrue(result)
        self.assertTrue("renamed" in result)
        self.assertEqual(len(result["renamed"]), 3)

    def test_get_target_folder(self):
        """测试获取目标文件夹功能"""
        # 测试已存在的映射
        def get_target_folder(folder_name, mapping):
            for key, value in mapping.items():
                if key in folder_name:
                    return os.path.join(self.target_dir, value)
            return os.path.join(self.target_dir, folder_name)

        target_folder = get_target_folder("陆雪琪", self.folder_mapping)
        self.assertEqual(target_folder, os.path.join(self.target_dir, "L_陆雪琪"))

        # 测试不存在的映射
        target_folder = get_target_folder("不存在的文件夹", self.folder_mapping)
        self.assertEqual(target_folder, os.path.join(self.target_dir, "不存在的文件夹"))

if __name__ == "__main__":
    unittest.main()