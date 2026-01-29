"""文件夹信息面板"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime


class FolderInfoPanel(ttk.Frame):
    """文件夹信息面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件夹信息面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, padding=20)
        self.main_app = main_app
        self.folder_paths = []

        # 创建滚动容器
        self.canvas = tk.Canvas(self, bg="#f5f5f5")
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=750)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 在滚动容器中创建控件
        self._create_widgets()
        self._setup_drag_drop()

    def _create_widgets(self):
        """创建控件"""
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(header_frame, text="📋 文件夹信息分析", font=("Microsoft YaHei", 14, "bold")).pack(anchor=tk.W)
        ttk.Label(header_frame, text="批量分析文件夹内所有文件的详细信息，支持导出为TXT和CSV格式",
                 font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=(5, 0))

        folder_frame = ttk.LabelFrame(self.scrollable_frame, text="文件夹列表", padding=10)
        folder_frame.pack(fill=tk.X, pady=10)

        self.folder_listbox = tk.Listbox(folder_frame, height=6, width=60, font=("Microsoft YaHei", 10),
                                         selectmode=tk.EXTENDED, bg="#ffffff")
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        scrollbar = ttk.Scrollbar(folder_frame, orient=tk.VERTICAL, command=self.folder_listbox.yview)
        self.folder_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = ttk.Frame(folder_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="+ 批量添加文件夹", command=self._browse_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="- 移除选中", command=self._remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空列表", command=self._clear_folders).pack(side=tk.LEFT, padx=5)

        hint_frame = ttk.Frame(folder_frame)
        hint_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(hint_frame, text="💡 提示: 您也可以直接将文件夹拖放到此窗口中进行添加",
                 font=("Microsoft YaHei", 8), foreground="#888888").pack(anchor=tk.W)

        option_frame = ttk.Frame(self.scrollable_frame)
        option_frame.pack(fill=tk.X, pady=10)

        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="递归子文件夹", variable=self.recursive_var).pack(side=tk.LEFT, padx=5)

        output_frame = ttk.LabelFrame(self.scrollable_frame, text="导出格式", padding=10)
        output_frame.pack(fill=tk.X, pady=10)

        self.export_format_var = tk.StringVar(value="txt")
        ttk.Radiobutton(output_frame, text="TXT 文本格式 (适合阅读)", variable=self.export_format_var,
                       value="txt").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(output_frame, text="CSV 表格格式 (适合Excel处理)", variable=self.export_format_var,
                       value="csv").pack(side=tk.LEFT, padx=10)

        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=10)

        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var,
                                        font=("Microsoft YaHei", 9))
        self.progress_label.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=100)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))

        result_frame = ttk.LabelFrame(self, text="分析结果预览", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_text = tk.Text(result_frame, height=10, width=60, font=("Courier New", 9),
                                   bg="#f5f5f5", state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="📊 详细文件分析", command=self._analyze_folders,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📤 导出文件", command=self._analyze_folders).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 快速结构分析", command=self._quick_analyze).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_all).pack(side=tk.RIGHT, padx=5)

    def _setup_drag_drop(self):
        """设置拖放支持"""
        # 暂时禁用拖放功能，避免启动失败
        # 拖放功能需要特定的Tkinter扩展支持
        print("拖放功能已禁用，避免启动失败")
        pass

    def _on_drop(self, event):
        """处理拖放事件"""
        try:
            data = event.data

            if data:
                # 尝试使用win32api解析拖放数据
                try:
                    import win32api
                    files = win32api.ParseCommandLine(data)
                except ImportError:
                    # 如果没有win32api，使用简单的字符串处理
                    files = [data.strip('"')]

                for file_path in files:
                    file_path = file_path.strip('"')
                    if os.path.isdir(file_path):
                        if file_path not in self.folder_paths:
                            self.folder_paths.append(file_path)
                            self.folder_listbox.insert(tk.END, file_path)
                            if hasattr(self, 'main_app'):
                                self.main_app.update_status(f"已添加文件夹: {os.path.basename(file_path)}")
        except Exception as e:
            # 拖放处理失败时静默失败
            print(f"拖放处理失败: {str(e)}")
            pass

    def _browse_folders(self):
        """浏览选择多个文件夹"""
        paths = filedialog.askdirectory(title="选择文件夹", initialdir=".", mustexist=True)
        if paths:
            if paths not in self.folder_paths:
                self.folder_paths.append(paths)
                self.folder_listbox.insert(tk.END, paths)
                self.main_app.update_status(f"已添加文件夹: {os.path.basename(paths)}")

    def _browse_folder(self):
        """浏览选择单个文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=".", mustexist=True)
        if path:
            if path not in self.folder_paths:
                self.folder_paths.append(path)
                self.folder_listbox.insert(tk.END, path)
            self.folder_path_var.set(path)

    def _remove_selected(self):
        """移除选中的文件夹"""
        selected = self.folder_listbox.curselection()
        if selected:
            for index in reversed(selected):
                path = self.folder_paths.pop(index)
                self.folder_listbox.delete(index)
                self.main_app.update_status(f"已移除: {os.path.basename(path)}")

    def _clear_folders(self):
        """清空文件夹列表"""
        self.folder_paths = []
        self.folder_listbox.delete(0, tk.END)
        self.main_app.update_status("已清空文件夹列表")

    def _analyze_folders(self):
        """分析文件夹"""
        if not self.folder_paths:
            self.main_app.show_message("提示", "请先添加要分析的文件夹", "info")
            return

        recursive = self.recursive_var.get()
        export_format = self.export_format_var.get()

        try:
            self.progress_var.set("正在分析文件夹...")
            self.progress_bar['value'] = 0
            self.root.update()

            from src.core.folder_info import export_to_txt, export_to_csv

            total_folders = len(self.folder_paths)

            for i, folder_path in enumerate(self.folder_paths):
                folder_name = os.path.basename(folder_path)
                self.progress_var.set(f"正在分析: {folder_name} ({i+1}/{total_folders})")
                self.progress_bar['value'] = (i / total_folders) * 100
                self.root.update()

            if export_format == "txt":
                output_path = export_to_txt(self.folder_paths, recursive=recursive)
            else:
                output_path = export_to_csv(self.folder_paths, recursive=recursive)

            self.progress_var.set(f"分析完成！结果已保存到: {output_path}")
            self.progress_bar['value'] = 100

            result_text = f"✅ 分析完成！\n\n输出文件: {output_path}\n分析文件夹数: {len(self.folder_paths)}\n递归模式: {'是' if recursive else '否'}\n导出格式: {'TXT' if export_format == 'txt' else 'CSV'}"

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            self.result_text.config(state=tk.DISABLED)

            self.main_app.update_status(f"文件分析完成，共处理 {len(self.folder_paths)} 个文件夹")

            if messagebox.askyesno("分析完成", f"分析结果已保存到:\n{output_path}\n\n是否打开文件？"):
                os.startfile(output_path)

        except Exception as e:
            self.progress_var.set(f"分析失败: {str(e)}")
            self.main_app.show_message("错误", f"分析失败: {str(e)}", "error")

    def _quick_analyze(self):
        """快速分析文件夹结构"""
        if not self.folder_paths:
            self.main_app.show_message("提示", "请先添加要分析的文件夹", "info")
            return

        try:
            from src.core.folder_info import analyze_folder_structure

            results = []
            for folder_path in self.folder_paths:
                result = analyze_folder_structure(folder_path, output_format="text")
                results.append(f"\n{'='*50}\n")
                results.append(result)

            full_result = "".join(results)

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, full_result)
            self.result_text.config(state=tk.DISABLED)

            self.main_app.update_status("快速分析完成")

        except Exception as e:
            self.main_app.show_message("错误", f"分析失败: {str(e)}", "error")

    def _clear_all(self):
        """清空所有"""
        self._clear_folders()
        self.recursive_var.set(True)
        self.export_format_var.set("txt")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.progress_var.set("就绪")
        self.progress_bar['value'] = 0
