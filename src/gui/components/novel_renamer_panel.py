"""小说文件重命名面板"""
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue

from src.utils.logger import get_logger

logger = get_logger(__name__)


def sanitize_filename(filename):
    """清理文件名，移除Windows不合法字符"""
    invalid_chars = r'[\\/:*?"<>|]'
    sanitized = re.sub(invalid_chars, '_', filename)
    sanitized = sanitized.strip('. ')
    if not sanitized:
        sanitized = "unnamed"
    return sanitized


def clean_text_line(line):
    """清理文本行，移除BOM、不可见字符和特殊控制字符"""
    if not line:
        return ""
    # 移除BOM和不可见字符
    line = line.replace('\ufeff', '').replace('\u200b', '').replace('\u3000', '')
    # 移除Windows行尾符 \r 和其他控制字符
    line = line.replace('\r', '').replace('\n', '')
    # 移除ASCII控制字符（0x00-0x1F 和 0x7F）
    line = re.sub(r'[\x00-\x1f\x7f]', '', line)
    # 移除零宽度字符和其他Unicode控制字符
    line = re.sub(r'[\u2000-\u200f\u2028-\u202f\u2060-\u206f]', '', line)
    return line.strip()


def parse_filename_for_book_info(filename):
    """从文件名中解析书名和作者（支持多种格式）"""
    # 格式1：《书名》作者.txt 或 《书名》作者：xxx.txt
    pattern1 = r'^《(.+?)》(.+?)\.txt$'
    match = re.match(pattern1, filename)
    if match:
        book_name = match.group(1).strip()
        author = match.group(2).strip()
        # 清理作者部分可能包含的"作者："等标记（保留"作者：不详"）
        if author != "作者：不详":
            author = re.sub(r'^[作者:：]\s*', '', author)
        return book_name, author

    # 格式2：书名 作者：xxx.txt （中间有空格分隔）
    pattern2 = r'^(.+?)\s+作者[：:]\s*(.+?)\.txt$'
    match = re.match(pattern2, filename)
    if match:
        book_name = match.group(1).strip()
        author = match.group(2).strip()
        # 清理书名中的多余符号
        book_name = re.sub(r'[《》【】\[\]]', '', book_name)
        return book_name, author

    # 格式3：书名 作者：不详.txt
    pattern3 = r'^(.+?)\s+作者[：:]\s*不详\.txt$'
    match = re.match(pattern3, filename)
    if match:
        book_name = match.group(1).strip()
        book_name = re.sub(r'[《》【】\[\]]', '', book_name)
        return book_name, "作者：不详"

    return None, None


def extract_book_info_from_text(lines):
    """从文本行中智能提取书名和作者"""
    book_name = None
    author = None

    # 定义常见的书名标记模式
    book_patterns = [
        r'^【(.+?)】',  # 【书名】
        r'^《(.+?)》',  # 《书名》
        r'^书名[：:]\s*(.+)$',  # 书名：xxx
        r'^书名\s+(.+)$',  # 书名 xxx
    ]

    # 定义常见的作者标记模式
    author_patterns = [
        r'^作者[：:]\s*(.+)$',  # 作者：xxx
        r'^作者\s+(.+)$',  # 作者 xxx
        r'^by\s+(.+)$',  # by xxx
        r'^作者名[：:]\s*(.+)$',  # 作者名：xxx
    ]

    # 先检查第一行是否包含单行格式："书名:xxx作者:xxx"（中间可能有\r或其他分隔符）
    if lines:
        first_line_clean = clean_text_line(lines[0])
        if first_line_clean:
            # 匹配单行格式：书名:xxx作者:xxx 或 书名:xxx\r作者:xxx
            # 使用非贪婪匹配，匹配到"作者"标记为止
            single_line_pattern = r'书名[：:]\s*(.+?)\s*作者[：:]\s*(.+)$'
            match = re.search(single_line_pattern, first_line_clean)
            if match:
                book_name = match.group(1).strip()
                author = match.group(2).strip()
                return book_name, author

    for line in lines[:30]:  # 检查前30行
        cleaned = clean_text_line(line)
        if not cleaned or len(cleaned) < 2:
            continue

        # 尝试提取书名
        if book_name is None:
            for pattern in book_patterns:
                match = re.match(pattern, cleaned)
                if match:
                    book_name = match.group(1).strip()
                    break

        # 尝试提取作者
        if author is None:
            for pattern in author_patterns:
                match = re.match(pattern, cleaned)
                if match:
                    author = match.group(1).strip()
                    break

        # 如果都找到了，提前退出
        if book_name and author:
            break

    # 如果没有找到明确的标记，使用前两行有意义的内容
    if book_name is None or author is None:
        meaningful_lines = []
        for line in lines[:20]:
            cleaned = clean_text_line(line)
            if cleaned and len(cleaned) >= 2:
                meaningful_lines.append(cleaned)

        if len(meaningful_lines) >= 2:
            if book_name is None:
                book_name = meaningful_lines[0]
            if author is None:
                author = meaningful_lines[1]
        elif len(meaningful_lines) == 1:
            if book_name is None:
                book_name = meaningful_lines[0]

    # 过滤掉明显不是书名/作者的内容
    if book_name:
        # 过滤太短或太长的书名
        if len(book_name) < 2 or len(book_name) > 100:
            book_name = None
        # 过滤包含网址、邮箱等的内容
        if re.search(r'http[s]?://|@|\.com|\.net', book_name):
            book_name = None

    if author:
        # 过滤太短或太长的作者名
        if len(author) < 1 or len(author) > 50:
            author = None
        # 过滤包含网址、邮箱等的内容
        if re.search(r'http[s]?://|@|\.com|\.net', author):
            author = None

    return book_name, author


def get_book_info(file_path):
    """从txt文件读取书名和作者，智能处理各种格式"""
    try:
        # 先检查文件名是否已经是正确格式
        filename = os.path.basename(file_path)
        book_name, author = parse_filename_for_book_info(filename)
        if book_name and author:
            return book_name, author

        # 如果文件名不是正确格式，从文件内容读取
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # 处理各种换行符格式：\r\n (Windows), \r (旧Mac), \n (Unix)
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            lines = content.split('\n')

            if not lines:
                return None, None

            book_name, author = extract_book_info_from_text(lines)

            if book_name and author:
                return book_name, author
            elif book_name:
                return book_name, "作者：不详"
            else:
                return None, None

    except Exception as e:
        logger.warning(f"读取文件失败 {file_path}: {str(e)}")
        return None, None


class NovelRenamerPanel(ttk.Frame):
    """小说文件重命名面板"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.folder_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.preview_data = []
        self.is_processing = False
        self.process_queue = queue.Queue()
        self.create_widgets()

    def create_widgets(self):
        """创建组件"""
        # 标题
        # title_label = ttk.Label(self, text="📚 小说文件重命名", font=('Microsoft YaHei', 16, 'bold'))
        # title_label.pack(pady=15)

        desc_label = ttk.Label(self, text="自动识别txt文件中的书名和作者，重命名为「《书名》作者.txt」格式",
                              font=('Microsoft YaHei', 10), foreground='#7f8c8d')
        desc_label.pack()

        # 文件夹选择
        folder_frame = ttk.Frame(self)
        folder_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(folder_frame, text="源文件夹:", font=('Microsoft YaHei', 11)).pack(side='left', padx=(0, 10))

        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, font=('Microsoft YaHei', 10), width=40)
        folder_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        browse_btn = ttk.Button(folder_frame, text="浏览", command=self.browse_folder)
        browse_btn.pack(side='right')

        # 输出文件夹选择
        output_frame = ttk.Frame(self)
        output_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(output_frame, text="输出文件夹:", font=('Microsoft YaHei', 11)).pack(side='left', padx=(0, 10))

        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, font=('Microsoft YaHei', 10), width=40)
        output_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        output_browse_btn = ttk.Button(output_frame, text="浏览", command=self.browse_output_folder)
        output_browse_btn.pack(side='right')

        self.use_same_folder_var = tk.BooleanVar(value=False)
        same_folder_check = ttk.Checkbutton(output_frame, text="使用源文件夹",
                                           variable=self.use_same_folder_var,
                                           command=self.on_same_folder_toggle)
        same_folder_check.pack(side='right', padx=10)

        # 选项
        options_frame = ttk.Frame(self)
        options_frame.pack(fill='x', padx=20, pady=5)

        self.skip_existing_var = tk.BooleanVar(value=True)
        skip_check = ttk.Checkbutton(options_frame, text="跳过已正确命名的文件（格式：《书名》作者.txt）",
                                    variable=self.skip_existing_var)
        skip_check.pack(side='left')

        # 按钮组
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=20, pady=10)

        self.preview_btn = ttk.Button(btn_frame, text="预览", command=self.preview_rename, state='disabled')
        self.preview_btn.pack(side='left', padx=(0, 10))

        self.rename_btn = ttk.Button(btn_frame, text="执行重命名", command=self.execute_rename, state='disabled')
        self.rename_btn.pack(side='left', padx=(0, 10))

        self.progress_label = ttk.Label(btn_frame, text="", font=('Microsoft YaHei', 10))
        self.progress_label.pack(side='left', padx=20)

        clear_btn = ttk.Button(btn_frame, text="清空", command=self.clear_all)
        clear_btn.pack(side='right')

        # 统计信息
        self.stats_frame = ttk.LabelFrame(self, text="统计信息")
        self.stats_frame.pack(fill='x', padx=20, pady=10)

        self.stats_label = ttk.Label(self.stats_frame, text="请选择文件夹并点击预览")
        self.stats_label.pack(padx=10, pady=5)

        # 文件列表
        list_frame = ttk.LabelFrame(self, text="文件列表（原名称 → 新名称）")
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('status', 'old_name', 'new_name', 'book_name', 'author')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)

        self.tree.heading('status', text='状态')
        self.tree.heading('old_name', text='原文件名')
        self.tree.heading('new_name', text='新文件名')
        self.tree.heading('book_name', text='书名')
        self.tree.heading('author', text='作者')

        self.tree.column('status', width=80, anchor='center')
        self.tree.column('old_name', width=180)
        self.tree.column('new_name', width=180)
        self.tree.column('book_name', width=150)
        self.tree.column('author', width=150)

        scrollbar_y = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # 日志区域
        log_frame = ttk.LabelFrame(self, text="操作日志")
        log_frame.pack(fill='x', padx=20, pady=10)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.pack(fill='both', expand=True)

    def on_same_folder_toggle(self):
        """当勾选使用源文件夹时触发"""
        if self.use_same_folder_var.get():
            self.output_path.set(self.folder_path.get())

    def log(self, message):
        """添加日志"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.update()

    def browse_folder(self):
        """浏览源文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.preview_btn.config(state='normal')
            if self.use_same_folder_var.get():
                self.output_path.set(folder)
            self.log(f"已选择源文件夹: {folder}")

    def browse_output_folder(self):
        """浏览输出文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)
            self.log(f"已选择输出文件夹: {folder}")

    def _is_already_correctly_named(self, filename):
        """检查文件名是否已经是正确格式"""
        book_name, author = parse_filename_for_book_info(filename)
        return book_name is not None and author is not None

    def _process_single_file(self, file_info):
        """处理单个文件（用于多线程）"""
        folder, filename = file_info
        file_path = os.path.join(folder, filename)

        # 先尝试从文件名解析书名和作者（支持多种格式）
        book_name, author = parse_filename_for_book_info(filename)

        if book_name and author:
            # 如果文件名已经包含正确的书名和作者信息
            new_filename = f"《{sanitize_filename(book_name)}》{sanitize_filename(author)}.txt"

            # 检查是否已经是标准格式，如果是则跳过
            if self.skip_existing_var.get() and filename == new_filename:
                return {
                    'old_path': file_path,
                    'old_name': filename,
                    'new_name': filename,
                    'book_name': book_name,
                    'author': author,
                    'status': '跳过'
                }
            # 否则需要重命名为标准格式
            return {
                'old_path': file_path,
                'old_name': filename,
                'new_name': new_filename,
                'book_name': book_name,
                'author': author,
                'status': '待重命名'
            }

        # 如果文件名不包含书名和作者信息，从文件内容读取
        book_name, author = get_book_info(file_path)
        if book_name is None:
            # 如果无法识别书名，使用原文件名（去掉扩展名）作为书名
            base_name = os.path.splitext(filename)[0]
            clean_book = sanitize_filename(base_name)
            new_filename = f"《{clean_book}》作者：不详.txt"
            return {
                'old_path': file_path,
                'old_name': filename,
                'new_name': new_filename,
                'book_name': base_name,
                'author': '作者：不详',
                'status': '待重命名'
            }

        clean_book = sanitize_filename(book_name)
        clean_author = sanitize_filename(author)
        new_filename = f"《{clean_book}》{clean_author}.txt"

        # 检查是否已经是正确名称
        if filename == new_filename:
            status = '跳过'
        else:
            status = '待重命名'

        return {
            'old_path': file_path,
            'old_name': filename,
            'new_name': new_filename,
            'book_name': book_name,
            'author': author,
            'status': status
        }

    def preview_rename(self):
        """预览重命名结果（使用多线程）"""
        folder = self.folder_path.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("错误", "请选择有效的源文件夹！")
            return

        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.preview_data = []
        txt_files = [f for f in os.listdir(folder) if f.lower().endswith('.txt')]

        if not txt_files:
            messagebox.showinfo("提示", "未找到txt文件！")
            return

        self.is_processing = True
        self.preview_btn.config(state='disabled')
        self.rename_btn.config(state='disabled')
        self.progress_label.config(text="正在处理...")
        self.log(f"找到 {len(txt_files)} 个txt文件，开始多线程处理...")

        # 使用多线程处理
        def process_files():
            results = []
            file_infos = [(folder, f) for f in txt_files]

            # 根据文件数量调整线程数
            max_workers = min(32, len(txt_files))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self._process_single_file, info): info for info in file_infos}

                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    try:
                        result = future.result()
                        results.append(result)
                        # 更新进度
                        self.after(0, lambda c=completed, t=len(txt_files):
                                  self.progress_label.config(text=f"处理进度: {c}/{t}"))
                    except Exception as e:
                        logger.error(f"处理文件失败: {str(e)}")
                        results.append({
                            'old_path': futures[future][1],
                            'old_name': futures[future][1],
                            'new_name': '-',
                            'book_name': '-',
                            'author': '-',
                            'status': '错误'
                        })

            return results

        def update_ui(results):
            """在主线程更新UI"""
            rename_count = 0
            skip_count = 0
            unknown_count = 0
            error_count = 0

            for result in results:
                self.tree.insert('', 'end', values=(
                    result['status'],
                    result['old_name'],
                    result['new_name'],
                    result['book_name'],
                    result['author']
                ))
                self.preview_data.append(result)

                if result['status'] == '待重命名':
                    rename_count += 1
                elif result['status'] == '跳过':
                    skip_count += 1
                elif result['status'] == '无法识别':
                    unknown_count += 1
                else:
                    error_count += 1

            self.stats_label.config(text=f"总数: {len(txt_files)} | 待重命名: {rename_count} | 跳过: {skip_count} | 无法识别: {unknown_count} | 错误: {error_count}")
            self.is_processing = False
            self.preview_btn.config(state='normal')

            if rename_count > 0:
                self.rename_btn.config(state='normal')

            self.progress_label.config(text="")
            self.log(f"预览完成！待重命名: {rename_count}个，跳过: {skip_count}个，无法识别: {unknown_count}个，错误: {error_count}个")

        # 在后台线程中处理
        thread = threading.Thread(target=lambda: update_ui(process_files()))
        thread.daemon = True
        thread.start()

    def execute_rename(self):
        """执行重命名"""
        if not self.preview_data:
            messagebox.showwarning("警告", "请先点击预览！")
            return

        output_folder = self.output_path.get()
        if not output_folder:
            messagebox.showwarning("警告", "请选择输出文件夹！")
            return

        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
                self.log(f"创建输出文件夹: {output_folder}")
            except Exception as e:
                messagebox.showerror("错误", f"创建输出文件夹失败: {str(e)}")
                return

        use_source_folder = self.use_same_folder_var.get()

        if use_source_folder:
            confirm_msg = "将在源文件夹中执行重命名，是否继续？"
        else:
            confirm_msg = f"重命名后的文件将保存到: {output_folder}\n是否继续？"

        if not messagebox.askyesno("确认", confirm_msg):
            return

        self.is_processing = True
        self.rename_btn.config(state='disabled')
        self.progress_label.config(text="正在重命名...")
        self.log("开始重命名...")

        def do_rename():
            success_count = 0
            skip_count = 0
            unknown_count = 0
            error_count = 0

            for i, item in enumerate(self.preview_data):
                if item['status'] == '跳过':
                    skip_count += 1
                    continue

                if item['status'] == '无法识别':
                    unknown_count += 1
                    continue

                if item['status'] == '错误':
                    error_count += 1
                    continue

                try:
                    old_path = item['old_path']

                    if use_source_folder:
                        new_path = os.path.join(os.path.dirname(old_path), item['new_name'])
                    else:
                        new_path = os.path.join(output_folder, item['new_name'])

                    # 处理重名文件
                    counter = 1
                    base_new_path = new_path
                    while os.path.exists(new_path):
                        name, ext = os.path.splitext(item['new_name'])
                        new_path = os.path.join(os.path.dirname(base_new_path),
                                               f"{name}_{counter}{ext}")
                        counter += 1

                    # 复制文件而不是移动（避免数据丢失）
                    with open(old_path, 'rb') as src_file:
                        content = src_file.read()
                    with open(new_path, 'wb') as dst_file:
                        dst_file.write(content)

                    success_count += 1
                    self.after(0, lambda p=i, t=len(self.preview_data):
                              self.progress_label.config(text=f"进度: {p+1}/{t}"))

                except Exception as e:
                    error_count += 1
                    self.after(0, lambda e=str(e): self.log(f"失败: {item['old_name']} - {e}"))
                    logger.error(f"重命名失败 {item['old_name']}: {str(e)}")

            return success_count, skip_count, unknown_count, error_count

        def update_ui_result(result):
            success, skip, unknown, error = result
            self.is_processing = False
            self.rename_btn.config(state='normal')
            self.progress_label.config(text="")
            self.log(f"完成！成功: {success}个，跳过: {skip}个，无法识别: {unknown}个，错误: {error}个")
            messagebox.showinfo("完成", f"重命名完成！\n成功: {success}个\n跳过: {skip}个\n无法识别: {unknown}个\n错误: {error}个")

        thread = threading.Thread(target=lambda: update_ui_result(do_rename()))
        thread.daemon = True
        thread.start()

    def clear_all(self):
        """清空所有"""
        self.folder_path.set('')
        self.output_path.set('')
        self.preview_data = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.log_text.delete(1.0, 'end')
        self.stats_label.config(text="请选择文件夹并点击预览")
        self.preview_btn.config(state='disabled')
        self.rename_btn.config(state='disabled')
        self.progress_label.config(text="")
        self.log("已清空")