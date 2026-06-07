"""Excel导出面板"""
import os
import tkinter as tk
from tkinter import ttk, filedialog
import threading


class ExcelExporterPanel(ttk.Frame):
    """Excel导出面板"""

    def __init__(self, parent, main_app):
        """
        初始化Excel导出面板
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

        ttk.Label(path_frame, text="文件夹路径:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=2)
        self.folder_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.folder_path_var, width=35).pack(fill=tk.X, pady=2)
        ttk.Button(path_frame, text="浏览", command=self._browse_folder).pack(side=tk.LEFT, pady=2)

        # 导出设置
        settings_frame = ttk.LabelFrame(self, text="导出设置", padding=10)
        settings_frame.pack(fill=tk.X, pady=10)

        # 导出名称
        name_frame = ttk.Frame(settings_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="导出名称:", font=("Microsoft YaHei", 10), width=10).pack(side=tk.LEFT, padx=5)
        self.export_name_var = tk.StringVar(value="文件清单")
        ttk.Entry(name_frame, textvariable=self.export_name_var, width=30).pack(fill=tk.X, padx=5)

        # 递归选项
        recursive_frame = ttk.Frame(settings_frame)
        recursive_frame.pack(fill=tk.X, pady=5)

        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(recursive_frame, text="递归子文件夹", variable=self.recursive_var).pack(anchor=tk.W, padx=5)

        # 包含缩略图选项
        thumbnails_frame = ttk.Frame(settings_frame)
        thumbnails_frame.pack(fill=tk.X, pady=5)

        self.thumbnails_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(thumbnails_frame, text="包含缩略图", variable=self.thumbnails_var).pack(anchor=tk.W, padx=5)

        # 导出结果
        result_frame = ttk.LabelFrame(self, text="导出结果", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(result_frame, text="导出日志:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.result_text = tk.Text(result_frame, height=8, width=50, font=("Courier New", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="导出Excel", command=self._export_excel, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

        # 提示标签
        ttk.Label(self, text="提示: 导出的Excel文件将保存在当前目录", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)

    def _export_excel(self):
        """导出Excel"""
        folder_path = self.folder_path_var.get().strip()
        export_name = self.export_name_var.get().strip()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        if not export_name:
            export_name = "文件清单"

        # 清空结果文本
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"开始导出 {export_name}...\n")
        self.main_app.update_status("正在导出Excel...")

        def export_thread():
            try:
                from src.core.excel_exporter import batch_export_folders
                result = batch_export_folders(
                    [folder_path],
                    export_name=export_name,
                    recursive=self.recursive_var.get(),
                    include_thumbnails=self.thumbnails_var.get()
                )

                if result:
                    self.result_text.insert(tk.END, f"导出成功: {result}\n")
                    self.main_app.show_message("成功", f"Excel导出成功: {result}", "success")
                    self.main_app.update_status(f"Excel导出成功: {result}")
                else:
                    self.result_text.insert(tk.END, "导出失败: 未生成Excel文件\n")
                    self.main_app.show_message("警告", "Excel导出失败", "warning")
                    self.main_app.update_status("Excel导出失败")
            except Exception as e:
                error_msg = f"导出失败: {str(e)}"
                self.result_text.insert(tk.END, f"{error_msg}\n")
                self.main_app.show_message("错误", error_msg, "error")
                self.main_app.update_status("Excel导出失败")

        # 启动后台线程
        thread = threading.Thread(target=export_thread)
        thread.daemon = True
        thread.start()

    def _clear_fields(self):
        """清空输入"""
        self.folder_path_var.set("")
        self.export_name_var.set("文件清单")
        self.recursive_var.set(True)
        self.thumbnails_var.set(False)
        self.result_text.delete(1.0, tk.END)
