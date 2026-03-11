"""图片属性编辑面板"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class ImagePropertyPanel(ttk.Frame):
    """图片属性编辑面板"""

    def __init__(self, parent, main_app):
        """
        初始化图片属性编辑面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, padding=20)
        self.main_app = main_app

        # 创建控件
        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 文件夹选择
        folder_frame = ttk.LabelFrame(self, text="文件夹选择", padding=10)
        folder_frame.pack(fill=tk.X, pady=10)

        ttk.Label(folder_frame, text="文件夹路径:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=2)
        self.folder_path_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_path_var, width=50).pack(fill=tk.X, pady=2)
        ttk.Button(folder_frame, text="浏览", command=self._browse_folder).pack(side=tk.LEFT, pady=2)

        # 递归选项
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(folder_frame, text="递归子文件夹", variable=self.recursive_var).pack(anchor=tk.W, pady=2)

        # 功能选项卡
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # 移除属性选项卡
        remove_tab = ttk.Frame(notebook)
        notebook.add(remove_tab, text="移除属性")

        # 移除属性选项
        ttk.Label(remove_tab, text="移除选项:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)

        self.remove_all_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(remove_tab, text="移除所有属性", variable=self.remove_all_var).pack(anchor=tk.W, pady=2)

        ttk.Label(remove_tab, text="属性列表:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.properties_listbox = tk.Listbox(remove_tab, height=10, width=40, font=("Courier New", 9))
        self.properties_listbox.pack(fill=tk.X, pady=2)

        # 常用属性列表
        common_properties = [
            # 图片属性
            "Title", "Author", "Subject", "Keywords", "Comments",
            "Artist", "Copyright", "Software", "DateTime",
            "Make", "Model", "ExposureTime", "FNumber", "ISO",
            "FocalLength", "GPSInfo", "Orientation", "DateTimeOriginal",
            # 音频属性
            "title", "artist", "album", "composer", "genre",
            "date", "comment", "year"
        ]
        for prop in common_properties:
            self.properties_listbox.insert(tk.END, prop)

        ttk.Button(remove_tab, text="移除选中属性", command=self._remove_selected_properties).pack(side=tk.LEFT, pady=5, padx=5)
        ttk.Button(remove_tab, text="移除所有属性", command=self._remove_all_properties).pack(side=tk.LEFT, pady=5, padx=5)

        # 添加属性选项卡
        add_tab = ttk.Frame(notebook)
        notebook.add(add_tab, text="添加属性")

        # 批量添加属性选项
        ttk.Label(add_tab, text="批量添加属性:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)

        # 单个属性添加
        single_prop_frame = ttk.Frame(add_tab)
        single_prop_frame.pack(fill=tk.X, pady=5)

        ttk.Label(single_prop_frame, text="属性名称:", font=("Microsoft YaHei", 9), width=10).pack(side=tk.LEFT, padx=5)
        self.property_name_var = tk.StringVar()
        property_names = [
            "Title", "Author", "Subject", "Keywords", "Comments",
            "Artist", "Copyright", "Software", "DateTime",
            "Album", "Composer", "Genre", "Year"
        ]
        ttk.Combobox(single_prop_frame, textvariable=self.property_name_var, values=property_names, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(single_prop_frame, text="属性值:", font=("Microsoft YaHei", 9), width=10).pack(side=tk.LEFT, padx=5)
        self.property_value_var = tk.StringVar()
        ttk.Entry(single_prop_frame, textvariable=self.property_value_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Button(single_prop_frame, text="添加", command=self._batch_add_property).pack(side=tk.LEFT, padx=5)

        # 多个属性添加
        multi_prop_frame = ttk.LabelFrame(add_tab, text="多个属性添加", padding=10)
        multi_prop_frame.pack(fill=tk.X, pady=10)

        ttk.Label(multi_prop_frame, text="属性列表:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=5)
        self.multi_properties_text = tk.Text(multi_prop_frame, height=6, width=60, font=("Courier New", 9))
        self.multi_properties_text.pack(fill=tk.X, pady=2)
        self.multi_properties_text.insert(tk.END, "# 格式: 属性名称=属性值\n# 每行一个属性\n# 示例:\n# Title=我的图片\n# Artist=用户\n# Copyright=版权所有")

        ttk.Button(multi_prop_frame, text="批量添加多个属性", command=self._batch_add_multiple_properties).pack(side=tk.LEFT, pady=5, padx=5)

        # 常用属性按钮
        ttk.Label(add_tab, text="常用属性:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        common_props_frame = ttk.Frame(add_tab)
        common_props_frame.pack(fill=tk.X, pady=2)

        ttk.Button(common_props_frame, text="作者", command=lambda: self._set_common_property("Artist")).pack(side=tk.LEFT, padx=5)
        ttk.Button(common_props_frame, text="标题", command=lambda: self._set_common_property("Title")).pack(side=tk.LEFT, padx=5)
        ttk.Button(common_props_frame, text="版权", command=lambda: self._set_common_property("Copyright")).pack(side=tk.LEFT, padx=5)

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self, textvariable=self.status_var, font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)

    def _remove_selected_properties(self):
        """移除选中的属性"""
        folder_path = self.folder_path_var.get().strip()
        if not folder_path:
            messagebox.showerror("错误", "请选择文件夹")
            return

        selected_indices = self.properties_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请选择要移除的属性")
            return

        selected_properties = [self.properties_listbox.get(i) for i in selected_indices]

        try:
            from src.core.image_property_editor import batch_remove_properties
            result = batch_remove_properties(
                folder_path,
                properties_to_remove=selected_properties,
                remove_all=False,
                recursive=self.recursive_var.get()
            )

            if result:
                self.status_var.set("移除属性完成")
                messagebox.showinfo("成功", "属性移除成功")
            else:
                self.status_var.set("移除属性失败")
                messagebox.showwarning("警告", "属性移除失败")
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")

    def _remove_all_properties(self):
        """移除所有属性"""
        folder_path = self.folder_path_var.get().strip()
        if not folder_path:
            messagebox.showerror("错误", "请选择文件夹")
            return

        try:
            from src.core.image_property_editor import batch_remove_properties
            result = batch_remove_properties(
                folder_path,
                remove_all=True,
                recursive=self.recursive_var.get()
            )

            if result:
                self.status_var.set("移除所有属性完成")
                messagebox.showinfo("成功", "所有属性移除成功")
            else:
                self.status_var.set("移除属性失败")
                messagebox.showwarning("警告", "属性移除失败")
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")

    def _batch_add_property(self):
        """批量添加属性"""
        folder_path = self.folder_path_var.get().strip()
        if not folder_path:
            messagebox.showerror("错误", "请选择文件夹")
            return

        property_name = self.property_name_var.get().strip()
        property_value = self.property_value_var.get().strip()

        if not property_name:
            messagebox.showerror("错误", "请输入属性名称")
            return

        if not property_value:
            messagebox.showerror("错误", "请输入属性值")
            return

        try:
            from src.core.image_property_editor import batch_add_property
            result = batch_add_property(
                folder_path,
                property_name,
                property_value,
                recursive=self.recursive_var.get()
            )

            if result:
                self.status_var.set("添加属性完成")
                messagebox.showinfo("成功", "属性添加成功")
            else:
                self.status_var.set("添加属性失败")
                messagebox.showwarning("警告", "属性添加失败")
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")

    def _set_common_property(self, property_name):
        """设置常用属性"""
        self.property_name_var.set(property_name)
        if property_name == "Artist":
            self.property_value_var.set("用户")
        elif property_name == "Title":
            self.property_value_var.set("未命名")
        elif property_name == "Copyright":
            self.property_value_var.set("版权所有")
        elif property_name == "Album":
            self.property_value_var.set("默认专辑")
        elif property_name == "Genre":
            self.property_value_var.set("未知")
        elif property_name == "Year":
            from datetime import datetime
            self.property_value_var.set(str(datetime.now().year))

    def _batch_add_multiple_properties(self):
        """批量添加多个属性"""
        folder_path = self.folder_path_var.get().strip()
        if not folder_path:
            messagebox.showerror("错误", "请选择文件夹")
            return

        # 获取属性列表文本
        properties_text = self.multi_properties_text.get(1.0, tk.END).strip()
        if not properties_text:
            messagebox.showerror("错误", "请输入属性列表")
            return

        # 解析属性列表
        properties = []
        for line in properties_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    prop_name, prop_value = line.split('=', 1)
                    properties.append((prop_name.strip(), prop_value.strip()))

        if not properties:
            messagebox.showerror("错误", "请输入有效的属性列表")
            return

        try:
            from src.core.image_property_editor import batch_add_property

            # 逐个添加属性
            total_success = 0
            total_failed = 0

            for prop_name, prop_value in properties:
                result = batch_add_property(
                    folder_path,
                    prop_name,
                    prop_value,
                    recursive=self.recursive_var.get()
                )
                if result:
                    total_success += 1
                else:
                    total_failed += 1

            if total_success > 0:
                self.status_var.set(f"添加 {total_success} 个属性完成")
                messagebox.showinfo("成功", f"成功添加 {total_success} 个属性")
            else:
                self.status_var.set("添加属性失败")
                messagebox.showwarning("警告", "属性添加失败")
        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")
