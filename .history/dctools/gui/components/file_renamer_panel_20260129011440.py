"""文件重命名面板"""
import tkinter as tk
from tkinter import ttk, filedialog


class FileRenamerPanel(ttk.LabelFrame):
    """文件重命名面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件重命名面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, text="✏️ 文件重命名", padding=20)
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

        # 中文名称输入
        name_frame = ttk.Frame(self)
        name_frame.pack(fill=tk.X, pady=10)

        ttk.Label(name_frame, text="中文名称:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=5)
        self.chinese_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.chinese_name_var, width=30).pack(side=tk.LEFT, padx=5)

        # 命名规则
        rule_frame = ttk.Frame(self)
        rule_frame.pack(fill=tk.X, pady=10)

        ttk.Label(rule_frame, text="命名规则:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.naming_rule_var = tk.StringVar(value="{type}_{pinyin_name}_{timestamp}_{index}")
        ttk.Entry(rule_frame, textvariable=self.naming_rule_var, width=60).pack(padx=5)

        # 预览
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(preview_frame, text="预览:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.preview_text = tk.Text(preview_frame, height=8, width=60, font=("Courier New", 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5)

        # 提示标签
        ttk.Label(self, text="提示: 支持变量 {pinyin_name}, {index}, {timestamp}, {type}, {chinese_name}", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="预览", command=self._preview_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重命名", command=self._rename_files, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)

    def _preview_rename(self):
        """预览重命名"""
        folder_path = self.folder_path_var.get().strip()
        chinese_name = self.chinese_name_var.get().strip()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        if not chinese_name:
            self.main_app.show_message("错误", "请输入中文名称", "error")
            return

        try:
            from dctools.core.file_renamer import preview_rename
            preview_list = preview_rename(folder_path, chinese_name)

            # 显示预览
            self.preview_text.delete(1.0, tk.END)
            for old_name, new_name in preview_list:
                self.preview_text.insert(tk.END, f"{old_name} -> {new_name}\n")

            self.main_app.update_status(f"预览完成，找到 {len(preview_list)} 个文件")
        except Exception as e:
            self.main_app.show_message("错误", f"预览失败: {str(e)}", "error")

    def _rename_files(self):
        """重命名文件"""
        folder_path = self.folder_path_var.get().strip()
        chinese_name = self.chinese_name_var.get().strip()
        naming_rule = self.naming_rule_var.get().strip()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        if not chinese_name:
            self.main_app.show_message("错误", "请输入中文名称", "error")
            return

        try:
            from dctools.core.file_renamer import batch_rename_files
            result = batch_rename_files(folder_path, chinese_name, naming_rule)

            if result:
                self.main_app.show_message("成功", f"成功重命名 {len(result)} 个文件", "success")
                self.main_app.update_status(f"成功重命名 {len(result)} 个文件")
            else:
                self.main_app.show_message("警告", "没有重命名任何文件", "warning")
        except Exception as e:
            self.main_app.show_message("错误", f"重命名失败: {str(e)}", "error")

    def _clear_fields(self):
        """清空输入"""
        self.folder_path_var.set("")
        self.chinese_name_var.set("")
        self.naming_rule_var.set("{type}_{pinyin_name}_{timestamp}_{index}")
        self.preview_text.delete(1.0, tk.END)
