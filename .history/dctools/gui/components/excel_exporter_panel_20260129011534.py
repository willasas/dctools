"""Excel导出面板"""
import tkinter as tk
from tkinter import ttk, filedialog


class ExcelExporterPanel(ttk.LabelFrame):
    """Excel导出面板"""

    def __init__(self, parent, main_app):
        """
        初始化Excel导出面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, text="📊 Excel导出", padding=20)
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

        # 导出名称
        name_frame = ttk.Frame(self)
        name_frame.pack(fill=tk.X, pady=10)

        ttk.Label(name_frame, text="导出名称:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
        self.export_name_var = tk.StringVar(value="文件清单")
        ttk.Entry(name_frame, textvariable=self.export_name_var, width=30).pack(side=tk.LEFT, padx=5)

        # 递归选项
        option_frame = ttk.Frame(self)
        option_frame.pack(fill=tk.X, pady=10)

        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="递归子文件夹", variable=self.recursive_var).pack(side=tk.LEFT, padx=5)

        # 预览
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(preview_frame, text="文件预览:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.preview_text = tk.Text(preview_frame, height=8, width=60, font=("Courier New", 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5)

        # 提示标签
        ttk.Label(self, text="提示: 导出文件将保存在 result 文件夹中", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="扫描", command=self._scan_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导出", command=self._export_excel, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)

    def _scan_files(self):
        """扫描文件"""
        folder_path = self.folder_path_var.get().strip()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        try:
            import os
            file_list = []
            recursive = self.recursive_var.get()

            if recursive:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        if not file.startswith('.'):
                            file_list.append(os.path.join(root, file))
            else:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isfile(item_path) and not item.startswith('.'):
                        file_list.append(item_path)

            # 显示预览
            self.preview_text.delete(1.0, tk.END)
            if file_list:
                for file_path in file_list[:50]:  # 只显示前50个文件
                    self.preview_text.insert(tk.END, f"{file_path}\n")
                if len(file_list) > 50:
                    self.preview_text.insert(tk.END, f"... 还有 {len(file_list) - 50} 个文件\n")
            else:
                self.preview_text.insert(tk.END, "没有找到文件\n")

            self.main_app.update_status(f"扫描完成，找到 {len(file_list)} 个文件")
        except Exception as e:
            self.main_app.show_message("错误", f"扫描失败: {str(e)}", "error")

    def _export_excel(self):
        """导出Excel"""
        folder_path = self.folder_path_var.get().strip()
        export_name = self.export_name_var.get().strip()
        recursive = self.recursive_var.get()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        try:
            from dctools.core.excel_exporter import batch_export_folders
            result = batch_export_folders([folder_path], export_name, recursive)

            if result:
                self.main_app.show_message("成功", f"Excel导出成功: {result}", "success")
                self.main_app.update_status(f"Excel导出成功")
            else:
                self.main_app.show_message("警告", "导出失败", "warning")
        except Exception as e:
            self.main_app.show_message("错误", f"导出失败: {str(e)}", "error")

    def _clear_fields(self):
        """清空输入"""
        self.folder_path_var.set("")
        self.export_name_var.set("文件清单")
        self.recursive_var.set(True)
        self.preview_text.delete(1.0, tk.END)
