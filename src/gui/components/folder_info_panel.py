"""文件夹信息分析面板"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading


class FolderInfoPanel(ttk.Frame):
    """文件夹信息分析面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件夹信息分析面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, padding=20)
        self.main_app = main_app
        self.folder_list = []

        # 创建控件
        self._create_widgets()
        # 尝试启用拖拽功能
        self._enable_drag_and_drop()

    def _create_widgets(self):
        """创建控件"""
        # 文件夹列表
        folder_frame = ttk.LabelFrame(self, text="文件夹列表", padding=10)
        folder_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 文件夹列表框
        self.folder_listbox = tk.Listbox(folder_frame, height=6, width=60, font=("Courier New", 10))
        self.folder_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # 文件夹操作按钮
        folder_btn_frame = ttk.Frame(folder_frame)
        folder_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(folder_btn_frame, text="添加文件夹", command=self._add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_btn_frame, text="移除文件夹", command=self._remove_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_btn_frame, text="清空列表", command=self._clear_folder_list).pack(side=tk.LEFT, padx=5)

        # 分析设置
        settings_frame = ttk.LabelFrame(self, text="分析设置", padding=10)
        settings_frame.pack(fill=tk.X, pady=10)

        # 递归选项
        recursive_frame = ttk.Frame(settings_frame)
        recursive_frame.pack(fill=tk.X, pady=5)

        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(recursive_frame, text="递归子文件夹", variable=self.recursive_var).pack(anchor=tk.W, padx=5)

        # 分析结果
        result_frame = ttk.LabelFrame(self, text="分析结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(result_frame, text="分析日志:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.result_text = tk.Text(result_frame, height=10, width=50, font=("Courier New", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 操作按钮
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(action_frame, text="分析文件夹", command=self._analyze_folders, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="导出到Excel", command=self._export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="分享", command=self._share_folder_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

        # 提示标签
        ttk.Label(self, text="提示: 支持拖拽文件夹到列表中进行分析", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

    def _enable_drag_and_drop(self):
        """启用拖拽功能"""
        try:
            from tkinterdnd2 import TkinterDnD, DND_FILES

            # 为列表框添加拖拽功能
            def drop(event):
                paths = event.data.split()
                for path in paths:
                    # 移除路径两端的引号
                    path = path.strip('"')
                    if os.path.isdir(path):
                        self._add_folder_to_list(path)

            # 绑定拖拽事件
            if hasattr(self.folder_listbox, 'drop_target_register'):
                self.folder_listbox.drop_target_register(DND_FILES)
                self.folder_listbox.dnd_bind('<<Drop>>', drop)
                print("拖拽功能已启用")
        except ImportError:
            print("tkinterdnd2 库不可用，拖拽功能已禁用")

    def _add_folder(self):
        """添加文件夹"""
        path = filedialog.askdirectory(title="选择文件夹")
        if path:
            self._add_folder_to_list(path)

    def _add_folder_to_list(self, path):
        """添加文件夹到列表"""
        if path not in self.folder_list:
            self.folder_list.append(path)
            self.folder_listbox.insert(tk.END, path)

    def _remove_folder(self):
        """移除选中的文件夹"""
        selected_index = self.folder_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            if index < len(self.folder_list):
                del self.folder_list[index]
                self.folder_listbox.delete(index)

    def _clear_folder_list(self):
        """清空文件夹列表"""
        self.folder_list.clear()
        self.folder_listbox.delete(0, tk.END)

    def _analyze_folders(self):
        """分析文件夹"""
        if not self.folder_list:
            self.main_app.show_message("错误", "请添加至少一个文件夹", "error")
            return

        # 清空结果文本
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"开始分析 {len(self.folder_list)} 个文件夹...\n")
        self.main_app.update_status("正在分析文件夹...")

        def analyze_thread():
            try:
                from src.core.folder_info import analyze_folder_structure

                for folder_path in self.folder_list:
                    self.result_text.insert(tk.END, f"\n分析文件夹: {folder_path}\n")
                    self.result_text.insert(tk.END, "-" * 50 + "\n")

                    result = analyze_folder_structure(folder_path, output_format="text", recursive=self.recursive_var.get())

                    if result:
                        self.result_text.insert(tk.END, result + "\n")
                    else:
                        self.result_text.insert(tk.END, "分析失败: 未获取到文件夹信息\n")

                self.main_app.update_status("文件夹分析完成")
            except Exception as e:
                error_msg = f"分析失败: {str(e)}"
                self.result_text.insert(tk.END, f"{error_msg}\n")
                self.main_app.show_message("错误", error_msg, "error")
                self.main_app.update_status("文件夹分析失败")

        # 启动后台线程
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()

    def _export_to_excel(self):
        """导出到Excel"""
        if not self.folder_list:
            self.main_app.show_message("错误", "请添加至少一个文件夹", "error")
            return

        self.main_app.update_status("正在导出Excel...")

        def export_thread():
            try:
                from src.core.excel_exporter import batch_export_folders

                result = batch_export_folders(
                    self.folder_list,
                    export_name="文件夹信息分析",
                    recursive=self.recursive_var.get(),
                    include_thumbnails=False
                )

                if result:
                    self.main_app.show_message("成功", f"Excel导出成功: {result}", "success")
                    self.main_app.update_status(f"Excel导出成功: {result}")
                else:
                    self.main_app.show_message("警告", "Excel导出失败", "warning")
                    self.main_app.update_status("Excel导出失败")
            except Exception as e:
                error_msg = f"导出失败: {str(e)}"
                self.main_app.show_message("错误", error_msg, "error")
                self.main_app.update_status("Excel导出失败")

        # 启动后台线程
        thread = threading.Thread(target=export_thread)
        thread.daemon = True
        thread.start()

    def _share_folder_info(self):
        """分享文件夹信息"""
        if not self.folder_list:
            self.main_app.show_message("错误", "请添加至少一个文件夹", "error")
            return

        # 这里可以实现分享功能，例如生成分享链接或复制到剪贴板
        self.main_app.show_message("提示", "分享功能开发中", "info")

    def _clear_fields(self):
        """清空输入"""
        self._clear_folder_list()
        self.recursive_var.set(True)
        self.result_text.delete(1.0, tk.END)
