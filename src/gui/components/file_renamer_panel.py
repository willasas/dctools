"""文件重命名面板"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import threading


class FileRenamerPanel(ttk.Frame):
    """文件重命名面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件重命名面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, padding=20)
        self.main_app = main_app

        # 重命名规则列表
        self.rename_rules = []

        # 创建控件
        self._create_widgets()

    def _create_widgets(self):
        """创建控件"""
        # 顶部布局：左侧基本选项，右侧移动选项
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=10)

        # 左侧：基本选项
        left_frame = ttk.LabelFrame(top_frame, text="基本选项", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # 文件夹路径选择
        path_frame = ttk.Frame(left_frame)
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_frame, text="文件夹路径:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=2)
        self.folder_path_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.folder_path_var, width=35).pack(fill=tk.X, pady=2)
        ttk.Button(path_frame, text="浏览", command=self._browse_folder).pack(side=tk.LEFT, pady=2)

        # 中文名称输入
        name_frame = ttk.Frame(left_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="中文名称:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=2)
        self.chinese_name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.chinese_name_var, width=35).pack(fill=tk.X, pady=2)

        # 右侧：移动选项
        right_frame = ttk.LabelFrame(top_frame, text="文件移动选项", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # 目标文件夹选择
        move_path_frame = ttk.Frame(right_frame)
        move_path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(move_path_frame, text="目标文件夹:", font=('Microsoft YaHei', 9)).pack(anchor=tk.W, pady=2)
        self.target_folder_var = tk.StringVar()
        ttk.Entry(move_path_frame, textvariable=self.target_folder_var, width=30).pack(fill=tk.X, pady=2)
        ttk.Button(move_path_frame, text="浏览", command=self._browse_target_folder).pack(side=tk.LEFT, pady=2)

        # 移动选项
        move_options_frame = ttk.Frame(right_frame)
        move_options_frame.pack(fill=tk.X, pady=5)

        self.after_rename_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(move_options_frame, text="重命名后自动移动", variable=self.after_rename_var).pack(anchor=tk.W, pady=2)

        self.overwrite_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(move_options_frame, text="覆盖已存在的文件", variable=self.overwrite_var).pack(anchor=tk.W, pady=2)

        # 命名规则
        rule_frame = ttk.Frame(self)
        rule_frame.pack(fill=tk.X, pady=10)

        # 左侧：命名规则输入
        rule_left_frame = ttk.Frame(rule_frame)
        rule_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(rule_left_frame, text="命名规则:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.naming_rule_var = tk.StringVar(value="{type}_{pinyin_name}_{timestamp}_{index}")
        ttk.Entry(rule_left_frame, textvariable=self.naming_rule_var, width=30).pack(fill=tk.X, padx=5)

        # 右侧：序号参数设置
        rule_right_frame = ttk.Frame(rule_frame)
        rule_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Label(rule_right_frame, text="序号参数:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)

        # 初始值
        start_value_frame = ttk.Frame(rule_right_frame)
        start_value_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_value_frame, text="初始值:", font=("Microsoft YaHei", 9), width=8).pack(side=tk.LEFT, padx=5)
        self.start_value_var = tk.StringVar(value="0")
        ttk.Entry(start_value_frame, textvariable=self.start_value_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(start_value_frame, text="(默认0)", font=("Microsoft YaHei", 8), foreground="#666666").pack(side=tk.LEFT)

        # 位数
        digits_frame = ttk.Frame(rule_right_frame)
        digits_frame.pack(fill=tk.X, pady=2)
        ttk.Label(digits_frame, text="位数:", font=("Microsoft YaHei", 9), width=8).pack(side=tk.LEFT, padx=5)
        self.digits_var = tk.StringVar(value="1")
        ttk.Entry(digits_frame, textvariable=self.digits_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(digits_frame, text="(默认1位)", font=("Microsoft YaHei", 8), foreground="#666666").pack(side=tk.LEFT)

        # 增量
        increment_frame = ttk.Frame(rule_right_frame)
        increment_frame.pack(fill=tk.X, pady=2)
        ttk.Label(increment_frame, text="增量:", font=("Microsoft YaHei", 9), width=8).pack(side=tk.LEFT, padx=5)
        self.increment_var = tk.StringVar(value="1")
        ttk.Entry(increment_frame, textvariable=self.increment_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(increment_frame, text="(默认1)", font=("Microsoft YaHei", 8), foreground="#666666").pack(side=tk.LEFT)

        # 高级重命名规则
        advanced_frame = ttk.LabelFrame(self, text="高级重命名规则", padding=10)
        advanced_frame.pack(fill=tk.X, pady=10)

        # 规则列表
        rules_list_frame = ttk.Frame(advanced_frame)
        rules_list_frame.pack(fill=tk.X, pady=5)

        ttk.Label(rules_list_frame, text="规则列表:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
        self.rules_listbox = tk.Listbox(rules_list_frame, height=5, width=60, font=("Courier New", 9))
        self.rules_listbox.pack(fill=tk.X, padx=5)

        # 规则操作按钮
        rules_btn_frame = ttk.Frame(advanced_frame)
        rules_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(rules_btn_frame, text="添加规则", command=self._add_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(rules_btn_frame, text="编辑规则", command=self._edit_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(rules_btn_frame, text="删除规则", command=self._delete_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(rules_btn_frame, text="清空规则", command=self._clear_rules).pack(side=tk.LEFT, padx=5)

        # 预览
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        ttk.Label(preview_frame, text="预览:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.preview_text = tk.Text(preview_frame, height=8, width=60, font=("Courier New", 10))
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5)

        # 进度条
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=10)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5)
        self.progress_label = ttk.Label(progress_frame, text="就绪", font=("Microsoft YaHei", 9), foreground="#666666")
        self.progress_label.pack(anchor=tk.W, padx=5, pady=2)

        # 提示标签
        ttk.Label(self, text="提示: 支持变量 {pinyin_name}, {index}, {timestamp}, {type}, {chinese_name}", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        self.preview_button = ttk.Button(button_frame, text="预览", command=self._preview_rename)
        self.preview_button.pack(side=tk.LEFT, padx=5)
        self.rename_button = ttk.Button(button_frame, text="重命名", command=self._rename_files, style="Primary.TButton")
        self.rename_button.pack(side=tk.LEFT, padx=5)
        self.move_button = ttk.Button(button_frame, text="移动文件", command=self._move_files, style="Accent.TButton")
        self.move_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)

    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)
            # 从文件夹路径中提取最后一个斜杠后的名称作为中文名称默认值
            folder_name = os.path.basename(path)
            self.chinese_name_var.set(folder_name)

    def _browse_target_folder(self):
        """浏览目标文件夹"""
        path = filedialog.askdirectory(title="选择目标文件夹", initialdir=self.target_folder_var.get() or ".")
        if path:
            self.target_folder_var.set(path)

    def _move_files(self):
        """移动文件"""
        folder_path = self.folder_path_var.get().strip()
        target_folder = self.target_folder_var.get().strip()

        if not folder_path:
            self.main_app.show_message("错误", "请选择源文件夹", "error")
            return

        if not target_folder:
            self.main_app.show_message("错误", "请选择目标文件夹", "error")
            return

        # 禁用按钮
        self.preview_button.config(state=tk.DISABLED)
        self.rename_button.config(state=tk.DISABLED)
        self.move_button.config(state=tk.DISABLED)

        # 更新进度条
        self.progress_var.set(0)
        self.progress_label.config(text="正在移动文件...")
        self.main_app.update_status("正在移动文件...")

        def move_thread():
            try:
                # 获取文件夹中的所有文件
                import os
                file_paths = []
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        file_paths.append(file_path)

                if not file_paths:
                    self.main_app.show_message("警告", "源文件夹中没有文件", "warning")
                    return

                # 预览移动
                from src.core.file_renamer import preview_move
                preview_result = preview_move(file_paths, target_folder)

                # 执行移动
                from src.core.file_renamer import batch_move_files
                result = batch_move_files(file_paths, target_folder, overwrite=self.overwrite_var.get())

                # 显示结果
                moved_count = len(result.get("moved", []))
                failed_count = len(result.get("failed", []))

                if moved_count > 0:
                    message = f"成功移动 {moved_count} 个文件"
                    if failed_count > 0:
                        message += f"，失败 {failed_count} 个文件"
                    self.main_app.show_message("成功", message, "success")
                    self.main_app.update_status(f"移动完成，成功 {moved_count} 个文件")
                else:
                    if failed_count > 0:
                        self.main_app.show_message("警告", f"没有移动任何文件，失败 {failed_count} 个文件", "warning")
                    else:
                        self.main_app.show_message("警告", "没有移动任何文件", "warning")

            except FileNotFoundError as e:
                self.main_app.show_message("错误", f"文件不存在: {str(e)}", "error")
            except NotADirectoryError as e:
                self.main_app.show_message("错误", f"路径不是文件夹: {str(e)}", "error")
            except PermissionError as e:
                self.main_app.show_message("错误", f"没有权限: {str(e)}", "error")
            except ValueError as e:
                self.main_app.show_message("错误", f"参数错误: {str(e)}", "error")
            except Exception as e:
                self.main_app.show_message("错误", f"移动失败: {str(e)}", "error")
            finally:
                # 启用按钮
                self.progress_var.set(100)
                self.progress_label.config(text="移动完成")
                self.preview_button.config(state=tk.NORMAL)
                self.rename_button.config(state=tk.NORMAL)
                self.move_button.config(state=tk.NORMAL)

        # 启动后台线程
        thread = threading.Thread(target=move_thread)
        thread.daemon = True
        thread.start()

    def _add_rule(self):
        """添加重命名规则"""
        # 创建规则类型选择对话框
        rule_types = [
            "添加前缀后缀",
            "替换文本",
            "正则表达式替换",
            "更改大小写",
            "删除括号内容",
            "更改扩展名",
            "移除空格",
            "添加日期时间",
            "添加随机字符串"
        ]

        # 创建选择窗口
        rule_window = tk.Toplevel(self)
        rule_window.title("添加规则")
        rule_window.geometry("400x300")
        rule_window.transient(self)
        rule_window.grab_set()

        # 计算并设置窗口位置在父窗口中间
        self.update_idletasks()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        window_width = 400
        window_height = 300

        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)

        rule_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 规则类型选择
        ttk.Label(rule_window, text="选择规则类型:", font=("Microsoft YaHei", 10)).pack(pady=10)
        rule_type_var = tk.StringVar(value=rule_types[0])
        rule_type_combo = ttk.Combobox(rule_window, textvariable=rule_type_var, values=rule_types, width=30)
        rule_type_combo.pack(pady=5)

        # 规则参数
        params_frame = ttk.Frame(rule_window)
        params_frame.pack(fill=tk.X, pady=10, padx=20)

        # 根据选择的规则类型显示不同的参数
        def update_params():
            # 清空参数框架
            for widget in params_frame.winfo_children():
                widget.destroy()

            rule_type = rule_type_var.get()

            if rule_type == "添加前缀后缀":
                ttk.Label(params_frame, text="前缀:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                prefix_var = tk.StringVar()
                ttk.Entry(params_frame, textvariable=prefix_var, width=30).pack(pady=2)

                ttk.Label(params_frame, text="后缀:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                suffix_var = tk.StringVar()
                ttk.Entry(params_frame, textvariable=suffix_var, width=30).pack(pady=2)

                ttk.Label(params_frame, text="后缀位置:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                position_var = tk.StringVar(value="before_ext")
                ttk.Combobox(params_frame, textvariable=position_var, values=["before_ext", "end"], width=28).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "prefix_suffix",
                        "prefix": prefix_var.get(),
                        "suffix": suffix_var.get(),
                        "position": position_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            elif rule_type == "替换文本":
                ttk.Label(params_frame, text="查找文本:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                find_var = tk.StringVar()
                ttk.Entry(params_frame, textvariable=find_var, width=30).pack(pady=2)

                ttk.Label(params_frame, text="替换文本:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                replace_var = tk.StringVar()
                ttk.Entry(params_frame, textvariable=replace_var, width=30).pack(pady=2)

                case_var = tk.BooleanVar(value=True)
                ttk.Checkbutton(params_frame, text="区分大小写", variable=case_var).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "replace",
                        "find": find_var.get(),
                        "replace": replace_var.get(),
                        "case_sensitive": case_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            elif rule_type == "更改大小写":
                ttk.Label(params_frame, text="大小写类型:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                case_type_var = tk.StringVar(value="title")
                ttk.Combobox(params_frame, textvariable=case_type_var, values=["lower", "upper", "title", "sentence"], width=28).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "case",
                        "case_type": case_type_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            elif rule_type == "删除括号内容":
                ttk.Label(params_frame, text="括号类型:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                brackets_frame = ttk.Frame(params_frame)
                brackets_frame.pack(fill=tk.X, pady=2)

                brackets_vars = {
                    "()": tk.BooleanVar(value=True),
                    "[]": tk.BooleanVar(value=True),
                    "{}": tk.BooleanVar(value=True)
                }

                for brackets, var in brackets_vars.items():
                    ttk.Checkbutton(brackets_frame, text=brackets, variable=var).pack(side=tk.LEFT, padx=10)

                def add_rule():
                    selected_brackets = [b for b, var in brackets_vars.items() if var.get()]
                    rule = {
                        "type": "remove_brackets",
                        "brackets_types": selected_brackets
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            elif rule_type == "更改扩展名":
                ttk.Label(params_frame, text="新扩展名:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                extension_var = tk.StringVar()
                ttk.Entry(params_frame, textvariable=extension_var, width=30).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "extension",
                        "new_extension": extension_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            elif rule_type == "移除空格":
                ttk.Label(params_frame, text="替换为:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                replace_with_var = tk.StringVar(value="_")
                ttk.Entry(params_frame, textvariable=replace_with_var, width=30).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "remove_spaces",
                        "replace_with": replace_with_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            elif rule_type == "添加日期时间":
                ttk.Label(params_frame, text="日期格式:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                format_var = tk.StringVar(value="%Y%m%d")
                ttk.Entry(params_frame, textvariable=format_var, width=30).pack(pady=2)

                ttk.Label(params_frame, text="添加位置:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                position_var = tk.StringVar(value="before_ext")
                ttk.Combobox(params_frame, textvariable=position_var, values=["before_ext", "start", "end"], width=28).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "add_datetime",
                        "format": format_var.get(),
                        "position": position_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            elif rule_type == "添加随机字符串":
                ttk.Label(params_frame, text="字符串长度:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                length_var = tk.StringVar(value="6")
                ttk.Entry(params_frame, textvariable=length_var, width=30).pack(pady=2)

                ttk.Label(params_frame, text="添加位置:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                position_var = tk.StringVar(value="before_ext")
                ttk.Combobox(params_frame, textvariable=position_var, values=["before_ext", "start", "end"], width=28).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "add_random_string",
                        "length": int(length_var.get()) if length_var.get().isdigit() else 6,
                        "position": position_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            else:  # 正则表达式替换
                ttk.Label(params_frame, text="正则表达式:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                pattern_var = tk.StringVar()
                ttk.Entry(params_frame, textvariable=pattern_var, width=30).pack(pady=2)

                ttk.Label(params_frame, text="替换文本:", font=("Microsoft YaHei", 9)).pack(anchor=tk.W, pady=2)
                replacement_var = tk.StringVar()
                ttk.Entry(params_frame, textvariable=replacement_var, width=30).pack(pady=2)

                def add_rule():
                    rule = {
                        "type": "regex",
                        "pattern": pattern_var.get(),
                        "replacement": replacement_var.get()
                    }
                    self.rename_rules.append(rule)
                    self._update_rules_list()
                    rule_window.destroy()

            # 添加按钮
            ttk.Button(params_frame, text="添加", command=add_rule).pack(pady=10)

        # 初始更新参数
        update_params()

        # 绑定规则类型变化事件
        rule_type_combo.bind("<<ComboboxSelected>>", lambda e: update_params())

    def _edit_rule(self):
        """编辑重命名规则"""
        selected_index = self.rules_listbox.curselection()
        if not selected_index:
            self.main_app.show_message("提示", "请选择要编辑的规则", "info")
            return

        index = selected_index[0]
        if index >= len(self.rename_rules):
            return

        rule = self.rename_rules[index]
        # 这里可以实现编辑规则的逻辑，与添加规则类似
        self.main_app.show_message("提示", "编辑规则功能开发中", "info")

    def _delete_rule(self):
        """删除重命名规则"""
        selected_index = self.rules_listbox.curselection()
        if not selected_index:
            self.main_app.show_message("提示", "请选择要删除的规则", "info")
            return

        index = selected_index[0]
        if index < len(self.rename_rules):
            del self.rename_rules[index]
            self._update_rules_list()

    def _clear_rules(self):
        """清空重命名规则"""
        self.rename_rules.clear()
        self._update_rules_list()

    def _update_rules_list(self):
        """更新规则列表显示"""
        self.rules_listbox.delete(0, tk.END)

        for i, rule in enumerate(self.rename_rules):
            rule_type = rule.get("type")

            if rule_type == "prefix_suffix":
                prefix = rule.get("prefix", "")
                suffix = rule.get("suffix", "")
                position = "扩展名前" if rule.get("position") == "before_ext" else "末尾"
                display_text = f"{i+1}. 添加前缀后缀: 前缀='{prefix}', 后缀='{suffix}', 位置={position}"
            elif rule_type == "replace":
                find = rule.get("find", "")
                replace = rule.get("replace", "")
                case = "区分大小写" if rule.get("case_sensitive") else "不区分大小写"
                display_text = f"{i+1}. 替换文本: '{find}' -> '{replace}', {case}"
            elif rule_type == "regex":
                pattern = rule.get("pattern", "")
                replacement = rule.get("replacement", "")
                display_text = f"{i+1}. 正则替换: '{pattern}' -> '{replacement}'"
            elif rule_type == "case":
                case_type = rule.get("case_type", "title")
                case_map = {
                    "lower": "小写",
                    "upper": "大写",
                    "title": "标题大小写",
                    "sentence": "句子首字母大写"
                }
                display_text = f"{i+1}. 更改大小写: {case_map.get(case_type, case_type)}"
            elif rule_type == "remove_brackets":
                brackets = ", ".join(rule.get("brackets_types", []))
                display_text = f"{i+1}. 删除括号内容: {brackets}"
            elif rule_type == "extension":
                ext = rule.get("new_extension", "")
                display_text = f"{i+1}. 更改扩展名: {ext}"
            elif rule_type == "remove_spaces":
                replace_with = rule.get("replace_with", "_")
                display_text = f"{i+1}. 移除空格: 替换为 '{replace_with}'"
            elif rule_type == "add_datetime":
                format = rule.get("format", "%Y%m%d")
                position_map = {
                    "before_ext": "扩展名前",
                    "start": "开头",
                    "end": "末尾"
                }
                position = position_map.get(rule.get("position"), "扩展名前")
                display_text = f"{i+1}. 添加日期时间: 格式='{format}', 位置={position}"
            elif rule_type == "add_random_string":
                length = rule.get("length", 6)
                position_map = {
                    "before_ext": "扩展名前",
                    "start": "开头",
                    "end": "末尾"
                }
                position = position_map.get(rule.get("position"), "扩展名前")
                display_text = f"{i+1}. 添加随机字符串: 长度={length}, 位置={position}"
            else:
                display_text = f"{i+1}. 未知规则类型"

            self.rules_listbox.insert(tk.END, display_text)

    def _preview_rename(self):
        """预览重命名"""
        folder_path = self.folder_path_var.get().strip()
        chinese_name = self.chinese_name_var.get().strip()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        # 禁用按钮
        self.preview_button.config(state=tk.DISABLED)
        self.rename_button.config(state=tk.DISABLED)
        self.move_button.config(state=tk.DISABLED)

        # 更新进度条
        self.progress_var.set(0)
        self.progress_label.config(text="正在预览文件...")
        self.main_app.update_status("正在预览文件...")

        def preview_thread():
            try:
                if self.rename_rules:
                    # 使用规则预览
                    from src.core.file_renamer import preview_rename_with_rules
                    preview_list = preview_rename_with_rules(folder_path, self.rename_rules, recursive=False)
                else:
                    # 使用传统命名规则预览
                    if not chinese_name:
                        self.main_app.show_message("错误", "请输入中文名称", "error")
                        return

                    # 获取序号参数
                    try:
                        start_value = int(self.start_value_var.get().strip()) if self.start_value_var.get().strip() else 0
                    except ValueError:
                        start_value = 0

                    try:
                        digits = int(self.digits_var.get().strip()) if self.digits_var.get().strip() else 1
                    except ValueError:
                        digits = 1

                    try:
                        increment = int(self.increment_var.get().strip()) if self.increment_var.get().strip() else 1
                    except ValueError:
                        increment = 1

                    from src.core.file_renamer import preview_rename
                    preview_list = preview_rename(folder_path, chinese_name, start_value=start_value, digits=digits, increment=increment)

                # 显示预览
                self.preview_text.delete(1.0, tk.END)
                for old_name, new_name in preview_list:
                    self.preview_text.insert(tk.END, f"{old_name} -> {new_name}\n")

                self.progress_var.set(100)
                self.progress_label.config(text="预览完成")
                self.main_app.update_status(f"预览完成，找到 {len(preview_list)} 个文件")
            except Exception as e:
                self.main_app.show_message("错误", f"预览失败: {str(e)}", "error")
                self.progress_label.config(text="预览失败")
            finally:
                # 启用按钮
                self.preview_button.config(state=tk.NORMAL)
                self.rename_button.config(state=tk.NORMAL)
                self.move_button.config(state=tk.NORMAL)

        # 启动后台线程
        thread = threading.Thread(target=preview_thread)
        thread.daemon = True
        thread.start()

    def _rename_files(self):
        """重命名文件"""
        folder_path = self.folder_path_var.get().strip()
        chinese_name = self.chinese_name_var.get().strip()
        naming_rule = self.naming_rule_var.get().strip()

        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return

        if not self.rename_rules and not chinese_name:
            self.main_app.show_message("错误", "请输入中文名称", "error")
            return

        # 禁用按钮
        self.preview_button.config(state=tk.DISABLED)
        self.rename_button.config(state=tk.DISABLED)
        self.move_button.config(state=tk.DISABLED)

        # 更新进度条
        self.progress_var.set(0)
        self.progress_label.config(text="正在重命名文件...")
        self.main_app.update_status("正在重命名文件...")

        def rename_thread():
            try:
                if self.rename_rules:
                    # 使用高级规则重命名
                    from src.core.file_renamer import batch_rename_with_rules
                    result = batch_rename_with_rules(folder_path, self.rename_rules, recursive=False)

                    # 检查是否有错误
                    if "error" in result:
                        self.main_app.show_message("错误", f"重命名失败: {result['error']}", "error")
                        return

                    renamed_count = len(result.get("renamed", []))
                    failed_count = len(result.get("failed", []))

                    if renamed_count > 0:
                        message = f"成功重命名 {renamed_count} 个文件"
                        if failed_count > 0:
                            message += f"，失败 {failed_count} 个文件"

                        # 重命名后自动移动
                        if self.after_rename_var.get():
                            target_folder = self.target_folder_var.get().strip()
                            if target_folder:
                                try:
                                    # 获取重命名后的文件路径
                                    renamed_files = []
                                    for old_name, new_name in result.get("renamed", []):
                                        renamed_file_path = os.path.join(folder_path, new_name)
                                        if os.path.exists(renamed_file_path):
                                            renamed_files.append(renamed_file_path)

                                    if renamed_files:
                                        from src.core.file_renamer import batch_move_files
                                        move_result = batch_move_files(renamed_files, target_folder, overwrite=self.overwrite_var.get())
                                        moved_count = len(move_result.get("moved", []))
                                        message += f"，并移动 {moved_count} 个文件到目标文件夹"
                                        self.main_app.update_status(f"成功重命名 {renamed_count} 个文件，移动 {moved_count} 个文件")
                                except Exception as e:
                                    self.main_app.show_message("警告", f"重命名成功但移动失败: {str(e)}", "warning")
                                    self.main_app.update_status(f"重命名成功，移动失败")
                            else:
                                self.main_app.show_message("警告", "重命名成功但未指定目标文件夹，无法自动移动", "warning")
                                self.main_app.update_status(f"重命名成功，未移动")
                        else:
                            self.main_app.update_status(f"成功重命名 {renamed_count} 个文件")

                        self.main_app.show_message("成功", message, "success")
                    else:
                        if failed_count > 0:
                            self.main_app.show_message("警告", f"没有重命名任何文件，失败 {failed_count} 个文件", "warning")
                        else:
                            self.main_app.show_message("警告", "没有重命名任何文件", "warning")
                else:
                    # 获取序号参数
                    try:
                        start_value = int(self.start_value_var.get().strip()) if self.start_value_var.get().strip() else 0
                    except ValueError:
                        start_value = 0

                    try:
                        digits = int(self.digits_var.get().strip()) if self.digits_var.get().strip() else 1
                    except ValueError:
                        digits = 1

                    try:
                        increment = int(self.increment_var.get().strip()) if self.increment_var.get().strip() else 1
                    except ValueError:
                        increment = 1

                    # 使用传统命名规则重命名
                    from src.core.file_renamer import batch_rename_files
                    result = batch_rename_files(folder_path, chinese_name, naming_rule, start_value=start_value, digits=digits, increment=increment)

                    if result:
                        # 重命名后自动移动
                        if self.after_rename_var.get():
                            target_folder = self.target_folder_var.get().strip()
                            if target_folder:
                                try:
                                    from src.core.file_renamer import batch_move_files
                                    move_result = batch_move_files(result, target_folder, overwrite=self.overwrite_var.get())
                                    moved_count = len(move_result.get("moved", []))
                                    self.main_app.show_message("成功", f"成功重命名 {len(result)} 个文件，并移动 {moved_count} 个文件到目标文件夹", "success")
                                    self.main_app.update_status(f"成功重命名 {len(result)} 个文件，移动 {moved_count} 个文件")
                                except Exception as e:
                                    self.main_app.show_message("警告", f"重命名成功但移动失败: {str(e)}", "warning")
                                    self.main_app.update_status(f"重命名成功，移动失败")
                            else:
                                self.main_app.show_message("警告", "重命名成功但未指定目标文件夹，无法自动移动", "warning")
                                self.main_app.update_status(f"重命名成功，未移动")
                        else:
                            self.main_app.show_message("成功", f"成功重命名 {len(result)} 个文件", "success")
                            self.main_app.update_status(f"成功重命名 {len(result)} 个文件")
                    else:
                        self.main_app.show_message("警告", "没有重命名任何文件", "warning")
            except FileNotFoundError as e:
                self.main_app.show_message("错误", f"文件不存在: {str(e)}", "error")
            except NotADirectoryError as e:
                self.main_app.show_message("错误", f"路径不是文件夹: {str(e)}", "error")
            except PermissionError as e:
                self.main_app.show_message("错误", f"没有权限: {str(e)}", "error")
            except ValueError as e:
                self.main_app.show_message("错误", f"参数错误: {str(e)}", "error")
            except Exception as e:
                self.main_app.show_message("错误", f"重命名失败: {str(e)}", "error")
            finally:
                # 启用按钮
                self.progress_var.set(100)
                self.progress_label.config(text="重命名完成")
                self.preview_button.config(state=tk.NORMAL)
                self.rename_button.config(state=tk.NORMAL)
                self.move_button.config(state=tk.NORMAL)

        # 启动后台线程
        thread = threading.Thread(target=rename_thread)
        thread.daemon = True
        thread.start()

    def _clear_fields(self):
        """清空输入"""
        self.folder_path_var.set("")
        self.chinese_name_var.set("")
        self.naming_rule_var.set("{type}_{pinyin_name}_{timestamp}_{index}")
        self.start_value_var.set("0")
        self.digits_var.set("1")
        self.increment_var.set("1")
        self.target_folder_var.set("")
        self.after_rename_var.set(False)
        self.overwrite_var.set(False)
        self.preview_text.delete(1.0, tk.END)
        self.rename_rules.clear()
        self._update_rules_list()
