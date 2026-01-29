"""文件去重面板"""
import tkinter as tk
from tkinter import ttk, filedialog


class DuplicateRemoverPanel(ttk.Frame):
    """文件去重面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件去重面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, padding=20)
        self.main_app = main_app

        # 创建控件
        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 文件夹路径选择
        path_frame = ttk.Frame(self)
        path_frame.pack(fill=tk.X, pady=10)

        ttk.Label(path_frame, text="文件夹路径:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
        self.folder_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.folder_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="浏览", command=self._browse_folder).pack(side=tk.LEFT, padx=5)

        # 去重方式和选项
        option_frame = ttk.LabelFrame(self, text="去重选项", padding=10)
        option_frame.pack(fill=tk.X, pady=10)

        # 去重方式
        method_subframe = ttk.Frame(option_frame)
        method_subframe.pack(fill=tk.X, pady=5)
        ttk.Label(method_subframe, text="去重方式:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
        self.method_var = tk.StringVar(value="hash")
        method_options = ["name", "size", "mtime", "hash"]
        ttk.Combobox(method_subframe, textvariable=self.method_var, values=method_options, width=10).pack(side=tk.LEFT, padx=5)

        # 递归选项
        recursive_subframe = ttk.Frame(option_frame)
        recursive_subframe.pack(fill=tk.X, pady=5)
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(recursive_subframe, text="递归子文件夹", variable=self.recursive_var).pack(side=tk.LEFT, padx=5)

        # 预览
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(preview_frame, text="重复文件预览:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.preview_text = tk.Text(preview_frame, height=10, width=60, font=("Courier New", 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5)

        # 提示标签
        ttk.Label(self, text="提示: hash方式最准确但速度较慢", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="扫描", command=self._preview_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=self._remove_duplicates, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)

    def _preview_duplicates(self):
        """预览重复文件"""
        folder_path = self.folder_path_var.get().strip()
        method = self.method_var.get()
        recursive = self.recursive_var.get()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        try:
            from src.core.duplicate_remover import preview_duplicates
            # 重定向输出到预览文本框
            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            try:
                removed_count = preview_duplicates(folder_path, method, recursive)
            finally:
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout

            # 显示预览
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, output)

            self.main_app.update_status(f"扫描完成，发现 {removed_count} 个重复文件")
        except Exception as e:
            self.main_app.show_message("错误", f"扫描失败: {str(e)}", "error")

    def _remove_duplicates(self):
        """删除重复文件"""
        folder_path = self.folder_path_var.get().strip()
        method = self.method_var.get()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        # 确认操作
        if not tk.messagebox.askyesno("确认", "确定要删除重复文件吗？此操作不可撤销。"):
            return

        try:
            from src.core.duplicate_remover import remove_duplicates
            removed_count = remove_duplicates(folder_path, method)

            if removed_count > 0:
                self.main_app.show_message("成功", f"成功删除 {removed_count} 个重复文件", "success")
                self.main_app.update_status(f"成功删除 {removed_count} 个重复文件")
                # 重新扫描以更新预览
                self._preview_duplicates()
            else:
                self.main_app.show_message("警告", "没有删除任何文件", "warning")
        except Exception as e:
            self.main_app.show_message("错误", f"删除失败: {str(e)}", "error")

    def _clear_fields(self):
        """清空输入"""
        self.folder_path_var.set("")
        self.method_var.set("hash")
        self.preview_text.delete(1.0, tk.END)
