"""文件夹创建面板"""
import os
import tkinter as tk
from tkinter import ttk, filedialog
import threading


class FolderCreatorPanel(ttk.Frame):
    """文件夹创建面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件夹创建面板
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

        ttk.Label(path_frame, text="父文件夹路径:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=2)
        self.folder_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.folder_path_var, width=35).pack(fill=tk.X, pady=2)
        ttk.Button(path_frame, text="浏览", command=self._browse_folder).pack(side=tk.LEFT, pady=2)

        # 文件夹名称列表
        name_frame = ttk.LabelFrame(self, text="文件夹名称列表", padding=10)
        name_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(name_frame, text="请输入文件夹名称（每行一个）:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.name_text = tk.Text(name_frame, height=10, width=50, font=("Courier New", 10))
        self.name_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="创建文件夹", command=self._create_folders, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

        # 提示标签
        ttk.Label(self, text="提示: 每行输入一个文件夹名称，支持批量创建", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择父文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)

    def _create_folders(self):
        """创建文件夹"""
        parent_path = self.folder_path_var.get().strip()
        name_text = self.name_text.get(1.0, tk.END).strip()

        if not parent_path:
            self.main_app.show_message("错误", "请选择父文件夹", "error")
            return

        if not name_text:
            self.main_app.show_message("错误", "请输入文件夹名称", "error")
            return

        # 解析文件夹名称列表
        folder_names = [name.strip() for name in name_text.split('\n') if name.strip()]

        if not folder_names:
            self.main_app.show_message("错误", "请输入有效的文件夹名称", "error")
            return

        # 禁用按钮
        self.main_app.update_status("正在创建文件夹...")

        def create_thread():
            try:
                from src.core.folder_creator import create_single_folder
                created_count = 0
                failed_count = 0

                for name in folder_names:
                    result = create_single_folder(name, parent_path)
                    if result:
                        created_count += 1
                    else:
                        failed_count += 1

                if created_count > 0:
                    message = f"成功创建 {created_count} 个文件夹"
                    if failed_count > 0:
                        message += f"，失败 {failed_count} 个文件夹"
                    self.main_app.show_message("成功", message, "success")
                    self.main_app.update_status(f"创建完成，成功 {created_count} 个文件夹")
                else:
                    self.main_app.show_message("警告", f"没有创建任何文件夹，失败 {failed_count} 个文件夹", "warning")
                    self.main_app.update_status("创建失败")
            except Exception as e:
                self.main_app.show_message("错误", f"创建失败: {str(e)}", "error")
                self.main_app.update_status("创建失败")

        # 启动后台线程
        thread = threading.Thread(target=create_thread)
        thread.daemon = True
        thread.start()

    def _clear_fields(self):
        """清空输入"""
        self.folder_path_var.set("")
        self.name_text.delete(1.0, tk.END)
