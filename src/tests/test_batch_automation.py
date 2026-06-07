#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量自动化功能测试
"""
import os
import json
import shutil
import tempfile
import unittest
from src.gui.components.batch_automation_panel import BatchAutomationPanel
import tkinter as tk

class TestBatchAutomation(unittest.TestCase):
    """批量自动化功能测试"""

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
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        
        # 创建批量自动化面板
        self.panel = BatchAutomationPanel(self.root, type('obj', (object,), {'theme': {'background': '#f0f0f0', 'foreground': '#000000'}, 'update_status': lambda *args: None}))

    def tearDown(self):
        """清理测试环境"""
        # 关闭主窗口
        self.root.destroy()
        
        # 删除临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_mapping_management(self):
        """测试映射管理功能"""
        # 测试加载默认映射
        self.assertTrue(len(self.panel.folder_mapping) > 0)
        
        # 测试添加映射
        test_key = "测试文件夹"
        test_value = "T_测试文件夹"
        self.panel.folder_mapping[test_key] = test_value
        self.assertEqual(self.panel.folder_mapping[test_key], test_value)
        
        # 测试保存映射
        self.panel._save_mapping()
        self.assertTrue(os.path.exists(self.panel.mapping_file))
        
        # 测试加载映射
        new_panel = BatchAutomationPanel(self.root, type('obj', (object,), {'theme': {'background': '#f0f0f0', 'foreground': '#000000'}, 'update_status': lambda *args: None}))
        self.assertEqual(new_panel.folder_mapping.get(test_key), test_value)

    def test_get_target_folder(self):
        """测试获取目标文件夹功能"""
        # 设置目标目录
        self.panel.target_dir.set(self.target_dir)
        
        # 测试已存在的映射
        target_folder = self.panel._get_target_folder("陆雪琪")
        self.assertEqual(target_folder, os.path.join(self.target_dir, "L_陆雪琪"))
        
        # 测试不存在的映射
        target_folder = self.panel._get_target_folder("不存在的文件夹")
        self.assertEqual(target_folder, os.path.join(self.target_dir, "不存在的文件夹"))

    def test_get_last_index(self):
        """测试获取最后序号功能"""
        # 创建测试目标文件夹
        test_target = os.path.join(self.target_dir, "L_陆雪琪")
        os.makedirs(test_target, exist_ok=True)
        
        # 创建测试文件
        with open(os.path.join(test_target, "picture_lu_xue_qi_20230101_00001.png"), "w") as f:
            f.write("test")
        with open(os.path.join(test_target, "picture_lu_xue_qi_20230101_00003.png"), "w") as f:
            f.write("test")
        
        # 测试获取最后序号
        last_index = self.panel._get_last_index(test_target)
        self.assertEqual(last_index, 3)

    def test_process_files(self):
        """测试处理文件功能"""
        # 设置源目录和目标目录
        self.panel.source_dir.set(self.source_dir)
        self.panel.target_dir.set(self.target_dir)
        
        # 执行处理
        self.panel._process_files(self.source_dir, self.target_dir)
        
        # 检查目标文件夹是否创建
        target_folder = os.path.join(self.target_dir, "L_陆雪琪")
        self.assertTrue(os.path.exists(target_folder))
        
        # 检查文件是否移动
        files_in_target = os.listdir(target_folder)
        self.assertTrue(len(files_in_target) > 0)

if __name__ == "__main__":
    unittest.main()