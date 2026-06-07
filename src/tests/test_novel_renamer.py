#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小说文件重命名功能测试
"""
import os
import sys
import shutil
import tempfile
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.gui.components.novel_renamer_panel import sanitize_filename, get_book_info, clean_text_line


class TestNovelRenamer(unittest.TestCase):
    """小说文件重命名功能测试"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

        # 创建测试txt文件（正常格式）
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("凡人修仙传\n")
            f.write("忘语\n")
            f.write("内容正文...\n")

    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_sanitize_filename(self):
        """测试文件名清理函数"""
        # 测试包含非法字符的文件名
        result = sanitize_filename("test\\file:name*?\"<>|.txt")
        # 反斜杠、冒号、星号、问号、双引号、<、>、| 共8个非法字符
        self.assertEqual(result, "test_file_name______.txt")

        # 测试首尾空格和点号
        result = sanitize_filename("  test file  .  ")
        self.assertEqual(result, "test file")

        # 测试空字符串
        result = sanitize_filename("")
        self.assertEqual(result, "unnamed")

    def test_clean_text_line(self):
        """测试文本行清理函数"""
        # 测试BOM移除
        result = clean_text_line("\ufeff凡人修仙传")
        self.assertEqual(result, "凡人修仙传")

        # 测试零宽空格移除
        result = clean_text_line("\u200b凡人修仙传\u200b")
        self.assertEqual(result, "凡人修仙传")

        # 测试普通空白字符
        result = clean_text_line("  凡人修仙传  ")
        self.assertEqual(result, "凡人修仙传")

    def test_get_book_info_normal(self):
        """测试获取书籍信息函数（正常格式）"""
        book_name, author = get_book_info(self.test_file)
        self.assertEqual(book_name, "凡人修仙传")
        self.assertEqual(author, "忘语")

    def test_get_book_info_with_bom(self):
        """测试获取书籍信息函数（含BOM）"""
        bom_file = os.path.join(self.temp_dir, "bom_test.txt")
        with open(bom_file, 'w', encoding='utf-8-sig') as f:
            f.write("凡人修仙传\n")
            f.write("忘语\n")

        book_name, author = get_book_info(bom_file)
        self.assertEqual(book_name, "凡人修仙传")
        self.assertEqual(author, "忘语")

    def test_get_book_info_with_metadata(self):
        """测试获取书籍信息函数（含元数据）"""
        # 文件开头有空行或元数据
        meta_file = os.path.join(self.temp_dir, "meta_test.txt")
        with open(meta_file, 'w', encoding='utf-8') as f:
            f.write("\ufeff\n")  # BOM行
            f.write("\n")  # 空行
            f.write("\u3000\n")  # 全角空格行
            f.write("斗破苍穹\n")  # 第一行有意义的
            f.write("天蚕土豆\n")  # 第二行有意义的

        book_name, author = get_book_info(meta_file)
        self.assertEqual(book_name, "斗破苍穹")
        self.assertEqual(author, "天蚕土豆")

    def test_get_book_info_only_book_name(self):
        """测试只有书名的文件"""
        single_line_file = os.path.join(self.temp_dir, "single.txt")
        with open(single_line_file, 'w', encoding='utf-8') as f:
            f.write("斗破苍穹\n")

        book_name, author = get_book_info(single_line_file)
        self.assertEqual(book_name, "斗破苍穹")
        self.assertEqual(author, "未知作者")

    def test_get_book_info_empty_file(self):
        """测试空文件"""
        empty_file = os.path.join(self.temp_dir, "empty.txt")
        with open(empty_file, 'w', encoding='utf-8') as f:
            pass

        book_name, author = get_book_info(empty_file)
        self.assertIsNone(book_name)
        self.assertIsNone(author)


if __name__ == "__main__":
    unittest.main()
