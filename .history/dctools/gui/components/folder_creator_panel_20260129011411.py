"""文件夹创建面板"""
import tkinter as tk
from tkinter import ttk, filedialog


class FolderCreatorPanel(ttk.LabelFrame):
    """文件夹创建面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件夹创建面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, text="📁 文件夹创建", padding=20)
        self.main_app = main_app

        # 创建控件
        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 父路径选择
        path_frame = ttk.Frame(self)
        path_frame.pack(fill=tk.X, pady=10)

        ttk.Label(path_frame, text="父路径:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
        self.parent_path_var = tk.StringVar(value=".")
        ttk.Entry(path_frame, textvariable=self.parent_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="浏览", command=self._browse_parent).pack(side=tk.LEFT, padx=5)

        # 文件夹名称列表
        name_frame = ttk.Frame(self)
        name_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(name_frame, text="文件夹名称列表:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.folder_names_text = tk.Text(name_frame, height=10, width=60, font=("Courier New", 10))
        self.folder_names_text.pack(fill=tk.BOTH, expand=True, padx=5)

        # 提示标签
        ttk.Label(self, text="提示: 每行输入一个文件夹名称", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="创建", command=self._create_folders, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

    def _browse_parent(self):
        """浏览父路径"""
        path = filedialog.askdirectory(title="选择父路径", initialdir=self.parent_path_var.get())
        if path:
            self.parent_path_var.set(path)

    def _create_folders(self):
        """创建文件夹"""
        parent_path = self.parent_path_var.get().strip()
        folder_names = self.folder_names_text.get(1.0, tk.END).strip().split('\n')

        if not folder_names or folder_names == ['']:
            self.main_app.show_message("错误", "请输入文件夹名称", "error")
            return

        created_count = 0
        for name in folder_names:
            name = name.strip()
            if name:
                try:
                    import os
                    folder_path = os.path.join(parent_path, name)
                    os.makedirs(folder_path, exist_ok=True)
                    created_count += 1
                except Exception as e:
                    self.main_app.show_message("错误", f"创建文件夹失败: {name} - {str(e)}", "error")

        if created_count > 0:
            self.main_app.show_message("成功", f"成功创建 {created_count} 个文件夹", "success")
            self.main_app.update_status(f"成功创建 {created_count} 个文件夹")
        else:
            self.main_app.show_message("警告", "没有创建任何文件夹", "warning")

    def _clear_fields(self):
        """清空输入"""
        self.folder_names_text.delete(1.0, tk.END)
