"""小说文件重命名面板"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text_line(line):
    """清理文本行，移除BOM和不可见字符"""
    if not line:
        return ""
    line = line.replace('\ufeff', '').replace('\u200b', '').replace('\u3000', '')
    line = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\r]', '', line)
    return line.strip()

def parse_filename_for_book_info(filename):
    """从文件名解析书名和作者"""
    name = os.path.splitext(filename)[0]

    patterns = [
        r'《(.+?)》(.+)',
        r'书名[：:]\s*([^\n\r]+)',
        r'作者[：:]\s*([^\n\r]+)',
        r'(.+?)\s+作者[：:]\s*(.+)',
        r'(.+?)\s+作者\s*(.+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            if len(match.groups()) == 2:
                book_name = match.group(1).strip()
                author = match.group(2).strip()
                if book_name and author:
                    return book_name, author
            elif len(match.groups()) == 1:
                return match.group(1).strip(), None

    return None, None

def get_book_info(file_path):
    """从txt文件读取书名和作者，智能处理各种格式"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        content = content.replace('\r\n', '\n').replace('\r', '\n')
        lines = content.split('\n')

        if not lines:
            return None, None

        meaningful_lines = []
        for i, line in enumerate(lines[:30]):
            cleaned = clean_text_line(line)
            if cleaned and len(cleaned) >= 2:
                meaningful_lines.append((i, cleaned))

        book_name = None
        author = None

        for line in meaningful_lines[:10]:
            text = line[1]
            match = re.search(r'书名[：:]\s*([^\n\r]+)', text)
            if match:
                book_name = match.group(1).strip()
                break

        for line in meaningful_lines[:10]:
            text = line[1]
            match = re.search(r'作者[：:]\s*([^\n\r]+)', text)
            if match:
                author = match.group(1).strip()
                break

        if not book_name and meaningful_lines:
            book_name = meaningful_lines[0][1]

        if not author and len(meaningful_lines) >= 2:
            second_line = meaningful_lines[1][1]
            if second_line and len(second_line) >= 2 and second_line != book_name:
                author = second_line

        return book_name, author

    except Exception as e:
        logger.warning(f"读取文件失败 {file_path}: {str(e)}")
        return None, None

class NovelRenamerPanel(ttk.Frame):
    """小说文件重命名面板"""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.file_list = []
        self.processed_results = []
        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 源路径
        source_frame = ttk.LabelFrame(self, text="源文件夹")
        source_frame.pack(fill=tk.X, padx=10, pady=5)

        self.source_entry = ttk.Entry(source_frame, width=60)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)

        source_browse_btn = ttk.Button(source_frame, text="浏览", command=self._browse_source)
        source_browse_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        # 输出路径
        output_frame = ttk.LabelFrame(self, text="输出文件夹")
        output_frame.pack(fill=tk.X, padx=10, pady=5)

        self.output_entry = ttk.Entry(output_frame, width=60)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)

        output_browse_btn = ttk.Button(output_frame, text="浏览", command=self._browse_output)
        output_browse_btn.pack(side=tk.RIGHT, padx=10, pady=5)

        # 选项
        options_frame = ttk.LabelFrame(self, text="选项")
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        self.skip_renamed_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="跳过已正确命名的文件（格式：《书名》作者.txt）",
                       variable=self.skip_renamed_var).pack(side=tk.LEFT, padx=10)

        # 按钮区域
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        preview_btn = ttk.Button(btn_frame, text="预览", command=self._preview)
        preview_btn.pack(side=tk.LEFT, padx=5)

        rename_btn = ttk.Button(btn_frame, text="执行重命名", command=self._rename)
        rename_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame, text="清空", command=self._clear)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 统计信息
        stats_frame = ttk.LabelFrame(self, text="统计信息")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_label = ttk.Label(stats_frame, text="总数: 0 | 待重命名: 0 | 跳过: 0 | 错误: 0")
        self.stats_label.pack(side=tk.LEFT, padx=10, pady=5)

        # 结果表格
        result_frame = ttk.LabelFrame(self, text="文件列表（原名称 → 新名称）")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('status', 'old_name', 'new_name', 'book_name', 'author')
        self.tree = ttk.Treeview(result_frame, columns=columns, show='headings')

        self.tree.heading('status', text='状态')
        self.tree.heading('old_name', text='原文件名')
        self.tree.heading('new_name', text='新文件名')
        self.tree.heading('book_name', text='书名')
        self.tree.heading('author', text='作者')

        self.tree.column('status', width=80)
        self.tree.column('old_name', width=250)
        self.tree.column('new_name', width=250)
        self.tree.column('book_name', width=150)
        self.tree.column('author', width=150)

        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def _browse_source(self):
        """浏览源文件夹"""
        path = filedialog.askdirectory()
        if path:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, path)

    def _browse_output(self):
        """浏览输出文件夹"""
        path = filedialog.askdirectory()
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    def _preview(self):
        """预览重命名结果"""
        source_path = self.source_entry.get().strip()
        if not source_path or not os.path.isdir(source_path):
            messagebox.showerror("错误", "请选择有效的源文件夹")
            return

        self.main_window.update_status("正在预览文件...", "info")

        self.file_list = [f for f in os.listdir(source_path)
                         if os.path.isfile(os.path.join(source_path, f)) and f.endswith('.txt')]

        self.processed_results = []

        def process_file(filename):
            file_path = os.path.join(source_path, filename)
            book_name, author = parse_filename_for_book_info(filename)

            if not book_name:
                book_name, author = get_book_info(file_path)

            if not book_name:
                book_name = os.path.splitext(filename)[0]

            if not author:
                author = "作者：不详"

            new_name = f"《{book_name}》{author}.txt"

            is_already_correct = False
            if self.skip_renamed_var.get():
                if re.match(r'《.+》.*\.txt$', filename):
                    is_already_correct = True

            return {
                'filename': filename,
                'file_path': file_path,
                'book_name': book_name,
                'author': author,
                'new_name': new_name,
                'status': '跳过' if is_already_correct else '待重命名'
            }

        with ThreadPoolExecutor(max_workers=4) as executor:
            self.processed_results = list(executor.map(process_file, self.file_list))

        self._update_tree()
        self._update_stats()

        self.main_window.update_status("预览完成", "success")

    def _update_tree(self):
        """更新结果表格"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for result in self.processed_results:
            self.tree.insert('', tk.END, values=(
                result['status'],
                result['filename'],
                result['new_name'],
                result['book_name'],
                result['author']
            ))

    def _update_stats(self):
        """更新统计信息"""
        total = len(self.processed_results)
        pending = sum(1 for r in self.processed_results if r['status'] == '待重命名')
        skipped = sum(1 for r in self.processed_results if r['status'] == '跳过')
        errors = sum(1 for r in self.processed_results if r['status'] == '错误')

        self.stats_label.config(text=f"总数: {total} | 待重命名: {pending} | 跳过: {skipped} | 错误: {errors}")

    def _rename(self):
        """执行重命名"""
        source_path = self.source_entry.get().strip()
        output_path = self.output_entry.get().strip()

        if not source_path or not os.path.isdir(source_path):
            messagebox.showerror("错误", "请选择有效的源文件夹")
            return

        if not output_path:
            output_path = source_path
        else:
            os.makedirs(output_path, exist_ok=True)

        if not self.processed_results:
            self._preview()

        self.main_window.update_status("正在重命名文件...", "info")

        success_count = 0
        fail_count = 0

        for result in self.processed_results:
            if result['status'] == '跳过':
                continue

            try:
                src = result['file_path']
                dst = os.path.join(output_path, result['new_name'])

                counter = 1
                while os.path.exists(dst):
                    name, ext = os.path.splitext(result['new_name'])
                    dst = os.path.join(output_path, f"{name}_{counter}{ext}")
                    counter += 1

                shutil.copy2(src, dst)
                success_count += 1
            except Exception as e:
                fail_count += 1
                logger.error(f"复制文件失败 {result['filename']}: {str(e)}")

        message = f"重命名完成！成功: {success_count} 个，失败: {fail_count} 个"
        self.main_window.update_status(message, "success")
        messagebox.showinfo("结果", message)

    def _clear(self):
        """清空输入"""
        self.source_entry.delete(0, tk.END)
        self.output_entry.delete(0, tk.END)
        self.file_list = []
        self.processed_results = []

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.stats_label.config(text="总数: 0 | 待重命名: 0 | 跳过: 0 | 错误: 0")
        self.main_window.update_status("已清空", "info")