"""批量自动化面板"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time

from src.utils.logger import get_logger
from src.core.duplicate_remover import remove_duplicates, preview_duplicates
from src.core.file_renamer import batch_rename_files

# 创建logger实例
logger = get_logger(__name__)

class BatchAutomationPanel(tk.Frame):
    """批量自动化面板"""

    def __init__(self, parent, main_window):
        """
        初始化批量自动化面板
        :param parent: 父容器
        :param main_window: 主窗口实例
        """
        super().__init__(parent)
        self.main_window = main_window
        self.theme = main_window.theme
        self.configure(bg=self.theme["background"])

        # 配置变量
        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.mapping_file = os.path.join(os.path.dirname(__file__), "..", "..", "config", "folder_mapping.json")
        self.folder_mapping = {}

        # 创建配置目录
        os.makedirs(os.path.join(os.path.dirname(__file__), "..", "..", "config"), exist_ok=True)

        # 创建UI
        self._create_ui()

        # 加载文件夹映射
        self._load_mapping()



    def _create_ui(self):
        """创建UI界面"""
        # 主容器
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="批量自动化处理",
            font=(("SimHei", 16, "bold")),
            foreground=self.theme["foreground"]
        )
        title_label.pack(pady=(0, 20))

        # 文件夹选择
        folder_frame = ttk.LabelFrame(main_frame, text="文件夹设置", padding="15")
        folder_frame.pack(fill=tk.X, pady=(0, 15))

        # 源文件夹
        source_frame = ttk.Frame(folder_frame)
        source_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(source_frame, text="源文件夹:", width=10).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(source_frame, textvariable=self.source_dir, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            source_frame,
            text="浏览",
            command=self._browse_source_dir,
            width=10
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # 目标文件夹
        target_frame = ttk.Frame(folder_frame)
        target_frame.pack(fill=tk.X)

        ttk.Label(target_frame, text="目标文件夹:", width=10).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(target_frame, textvariable=self.target_dir, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            target_frame,
            text="浏览",
            command=self._browse_target_dir,
            width=10
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # 文件夹映射管理
        mapping_frame = ttk.LabelFrame(main_frame, text="文件夹映射管理", padding="15")
        mapping_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # 映射列表
        self.mapping_tree = ttk.Treeview(
            mapping_frame,
            columns=("key", "value"),
            show="headings"
        )
        self.mapping_tree.heading("key", text="源文件夹")
        self.mapping_tree.heading("value", text="目标文件夹")
        self.mapping_tree.column("key", width=200)
        self.mapping_tree.column("value", width=300)

        # 滚动条
        scrollbar = ttk.Scrollbar(mapping_frame, orient=tk.VERTICAL, command=self.mapping_tree.yview)
        self.mapping_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mapping_tree.pack(fill=tk.BOTH, expand=True)

        # 映射操作按钮
        mapping_buttons_frame = ttk.Frame(mapping_frame)
        mapping_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            mapping_buttons_frame,
            text="添加映射",
            command=self._add_mapping,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            mapping_buttons_frame,
            text="编辑映射",
            command=self._edit_mapping,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            mapping_buttons_frame,
            text="删除映射",
            command=self._delete_mapping,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            mapping_buttons_frame,
            text="保存映射",
            command=self._save_mapping,
            width=15
        ).pack(side=tk.LEFT)

        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(
            button_frame,
            text="开始处理",
            command=self._start_process,
            width=20,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="预览",
            command=self._preview_process,
            width=20
        ).pack(side=tk.LEFT)

        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="15")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            log_frame,
            height=10,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="#f0f0f0"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscroll=log_scrollbar.set)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 加载映射到树视图
        self._update_mapping_tree()

    def _browse_source_dir(self):
        """浏览源文件夹"""
        dir_path = filedialog.askdirectory(title="选择源文件夹")
        if dir_path:
            self.source_dir.set(dir_path)

    def _browse_target_dir(self):
        """浏览目标文件夹"""
        dir_path = filedialog.askdirectory(title="选择目标文件夹")
        if dir_path:
            self.target_dir.set(dir_path)

    def _load_mapping(self):
        """加载文件夹映射"""
        try:
            if os.path.exists(self.mapping_file):
                with open(self.mapping_file, "r", encoding="utf-8") as f:
                    self.folder_mapping = json.load(f)
            else:
                # 默认映射
                self.folder_mapping = {
                    "云望舒": "Y_云望舒",
                    "炽阳华明": "C_炽阳华明",
                    "燕倾菲": "Y_燕倾菲",
                    "月皇": "Y_月皇",
                    "兰若": "L_兰若",
                    "姚惜雪": "Y_姚惜雪",
                    "李慕婉": "L_李慕婉",
                    "红蝶": "H_红蝶",
                    "赵欣梦": "Z_赵欣梦",
                    "魅姬": "M_魅姬",
                    "雷电将军": "L_雷电将军",
                    "徐欣": "X_徐欣",
                    "魄瑜候": "P_魄瑜候",
                    "潮女妖": "C_潮女妖",
                    "焰灵姬": "Y_焰灵姬",
                    "云曦": "Y_云曦",
                    "叶倾仙": "Y_叶倾仙",
                    "晓月仙子": "X_晓月仙子",
                    "月婵": "Y_月婵",
                    "月柳": "Y_月柳",
                    "柳神": "L_柳神",
                    "清漪": "Q_清漪",
                    "火灵儿": "H_火灵儿",
                    "狠人大帝": "H_狠人大帝",
                    "王曦": "W_王曦",
                    "莫仙": "M_莫仙",
                    "蓝仙": "L_蓝仙",
                    "虚天神藤": "S_神藤",
                    "邀月": "Y_邀月公主",
                    "雪琳": "X_雪琳",
                    "魔女": "M_魔女",
                    "龙女": "L_龙女",
                    "云霄": "Y_云霄",
                    "女娲": "N_女娲",
                    "姮娥": "H_姮娥",
                    "姜力": "J_姜立",
                    "姜立": "J_姜立",
                    "左秋琳": "Z_左秋琳",
                    "穆红绫": "M_穆红绫",
                    "绫清竹": "L_绫清竹",
                    "幽千雪": "Y_幽千雪",
                    "南宫锦": "N_南宫锦",
                    "圣采儿": "S_圣采儿",
                    "周小环": "Z_周小环",
                    "小白": "X_小白",
                    "碧瑶": "B_碧瑶",
                    "陆雪琪": "L_陆雪琪",
                    "姚曦": "Y_姚曦",
                    "姬紫月": "J_姬紫月",
                    "安妙依": "A_安妙依",
                    "瑶池圣女": "Y_瑶池圣女",
                    "紫府圣女": "Z_紫府圣女",
                    "薇薇": "W_薇薇",
                    "西王母": "X_西王母",
                    "阴阳圣女": "Y_阴阳圣女",
                    "刘月": "L_刘月",
                    "燕倾城": "Y_燕倾城",
                    "赵琳儿": "Z_赵琳儿",
                    "梦千秋": "M_梦千秋"
                }
                # 保存默认映射
                self._save_mapping()
        except Exception as e:
            print(f"加载映射文件失败: {str(e)}")
            self.folder_mapping = {}

    def _save_mapping(self):
        """保存文件夹映射"""
        try:
            with open(self.mapping_file, "w", encoding="utf-8") as f:
                json.dump(self.folder_mapping, f, ensure_ascii=False, indent=2)
            # 检查log_text是否存在
            if hasattr(self, 'log_text'):
                self.log("映射文件保存成功", "success")
            else:
                print("映射文件保存成功")
        except Exception as e:
            # 检查log_text是否存在
            if hasattr(self, 'log_text'):
                self.log(f"保存映射文件失败: {str(e)}", "error")
            else:
                print(f"保存映射文件失败: {str(e)}")

    def _update_mapping_tree(self):
        """更新映射树视图"""
        # 清空树视图
        for item in self.mapping_tree.get_children():
            self.mapping_tree.delete(item)

        # 添加映射
        for key, value in self.folder_mapping.items():
            self.mapping_tree.insert("", tk.END, values=(key, value))

    def _add_mapping(self):
        """添加映射"""
        # 创建添加映射对话框
        dialog = tk.Toplevel(self)
        dialog.title("添加映射")
        dialog.geometry("400x250")

        # 居中显示弹窗
        dialog.transient(self)
        dialog.grab_set()

        # 计算弹窗位置
        self.update_idletasks()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        dialog_width = 400
        dialog_height = 250

        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # 源文件夹
        ttk.Label(dialog, text="源文件夹:", width=10).pack(padx=20, pady=(20, 5))
        source_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=source_var, width=40).pack(padx=20, pady=(0, 15))

        # 目标文件夹
        ttk.Label(dialog, text="目标文件夹:", width=10).pack(padx=20, pady=(0, 5))
        target_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=target_var, width=40).pack(padx=20, pady=(0, 20))

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # 创建一个容器来居中按钮
        button_container = ttk.Frame(button_frame)
        button_container.pack(side=tk.TOP, anchor=tk.CENTER, pady=10)

        def on_ok():
            source = source_var.get().strip()
            target = target_var.get().strip()
            if source and target:
                self.folder_mapping[source] = target
                self._update_mapping_tree()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "源文件夹和目标文件夹不能为空")

        ttk.Button(button_container, text="确定", command=on_ok, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_container, text="取消", command=dialog.destroy, width=15).pack(side=tk.LEFT)

    def _edit_mapping(self):
        """编辑映射"""
        selected_item = self.mapping_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择要编辑的映射")
            return

        item = selected_item[0]
        values = self.mapping_tree.item(item, "values")
        source = values[0]
        target = values[1]

        # 创建编辑映射对话框
        dialog = tk.Toplevel(self)
        dialog.title("编辑映射")
        dialog.geometry("400x250")

        # 居中显示弹窗
        dialog.transient(self)
        dialog.grab_set()

        # 计算弹窗位置
        self.update_idletasks()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        dialog_width = 400
        dialog_height = 250

        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)

        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # 源文件夹
        ttk.Label(dialog, text="源文件夹:", width=10).pack(padx=20, pady=(20, 5))
        source_var = tk.StringVar(value=source)
        ttk.Entry(dialog, textvariable=source_var, width=40).pack(padx=20, pady=(0, 15))

        # 目标文件夹
        ttk.Label(dialog, text="目标文件夹:", width=10).pack(padx=20, pady=(0, 5))
        target_var = tk.StringVar(value=target)
        ttk.Entry(dialog, textvariable=target_var, width=40).pack(padx=20, pady=(0, 20))

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # 创建一个容器来居中按钮
        button_container = ttk.Frame(button_frame)
        button_container.pack(side=tk.TOP, anchor=tk.CENTER, pady=10)

        def on_ok():
            new_source = source_var.get().strip()
            new_target = target_var.get().strip()
            if new_source and new_target:
                # 删除旧映射
                del self.folder_mapping[source]
                # 添加新映射
                self.folder_mapping[new_source] = new_target
                self._update_mapping_tree()
                dialog.destroy()
            else:
                messagebox.showerror("错误", "源文件夹和目标文件夹不能为空")

        ttk.Button(button_container, text="确定", command=on_ok, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_container, text="取消", command=dialog.destroy, width=15).pack(side=tk.LEFT)

    def _delete_mapping(self):
        """删除映射"""
        selected_item = self.mapping_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择要删除的映射")
            return

        item = selected_item[0]
        values = self.mapping_tree.item(item, "values")
        source = values[0]

        if messagebox.askyesno("确认", f"确定要删除映射 '{source}' 吗？"):
            if source in self.folder_mapping:
                del self.folder_mapping[source]
                self._update_mapping_tree()

    def _get_target_folder(self, folder_name):
        """根据文件夹名称获取目标文件夹"""
        for key, value in self.folder_mapping.items():
            if key in folder_name:
                return os.path.join(self.target_dir.get(), value)
        # 如果没有匹配的映射，返回原文件夹名
        return os.path.join(self.target_dir.get(), folder_name)

    def _get_last_index(self, folder_path):
        """获取文件夹中最后一张图片的序号"""
        if not os.path.exists(folder_path):
            return 0

        files = os.listdir(folder_path)
        if not files:
            return 0

        # 匹配命名规则的文件
        import re
        pattern = r'^\w+_\w+_\d+_(\d+)\.\w+$'
        max_index = 0

        for file in files:
            match = re.match(pattern, file)
            if match:
                try:
                    index = int(match.group(1))
                    if index > max_index:
                        max_index = index
                except ValueError:
                    pass

        return max_index

    def _start_process(self):
        """开始处理"""
        source_dir = self.source_dir.get().strip()
        target_dir = self.target_dir.get().strip()

        if not source_dir:
            messagebox.showwarning("警告", "请选择源文件夹")
            return

        if not target_dir:
            messagebox.showwarning("警告", "请选择目标文件夹")
            return

        if not os.path.exists(source_dir):
            messagebox.showerror("错误", f"源文件夹不存在: {source_dir}")
            return

        # 创建目标目录
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
                self.log(f"创建目标目录: {target_dir}")
            except Exception as e:
                messagebox.showerror("错误", f"创建目标目录失败: {str(e)}")
                return

        # 开始处理
        self.log("开始批量自动化处理...")
        self.log(f"源目录: {source_dir}")
        self.log(f"目标目录: {target_dir}")

        # 启动处理线程
        threading.Thread(target=self._process_files, args=(source_dir, target_dir), daemon=True).start()

    def _process_files(self, source_dir, target_dir):
        """处理文件"""
        try:
            # 遍历源目录下的所有子文件夹
            for item in os.listdir(source_dir):
                source_path = os.path.join(source_dir, item)
                if os.path.isdir(source_path):
                    target_path = self._get_target_folder(item)
                    self.log(f"\n开始处理文件夹: {item}")

                    # 创建目标文件夹
                    if not os.path.exists(target_path):
                        os.makedirs(target_path)
                        self.log(f"创建目标文件夹: {target_path}")

                    # 检查重复文件并展示
                    self.log("正在检查重复文件...")
                    try:
                        duplicate_count, preview_details = preview_duplicates(source_path, method="hash", recursive=False)
                        self.log(f"发现 {duplicate_count} 个重复文件")
                        if duplicate_count > 0:
                            self.log("重复文件组:")
                            for detail in preview_details:
                                self.log(detail)
                            # 自动删除重复文件（在测试环境中避免对话框）
                            remove_duplicates(source_path, method="hash", recursive=False)
                            self.log("重复文件已删除")
                    except Exception as e:
                        self.log(f"检查重复文件失败: {str(e)}", "error")

                    # 获取初始值
                    last_index = self._get_last_index(target_path)
                    start_value = last_index + 1
                    self.log(f"初始序号: {start_value}")

                    # 重命名并移动
                    self.log("正在重命名和移动文件...")
                    try:
                        # 使用目标文件夹的名称作为中文名称
                        target_folder_name = os.path.basename(target_path)
                        # 去除目标文件夹名称中的前缀（如Y_）
                        if '_' in target_folder_name:
                            chinese_name = target_folder_name.split('_', 1)[1]
                        else:
                            chinese_name = target_folder_name

                        # 重命名文件
                        result = batch_rename_files(
                            source_path,
                            chinese_name,
                            naming_rule="{type}_{pinyin_name}_{timestamp}_{index}",
                            start_value=start_value,
                            digits=5,
                            increment=1
                        )

                        if result and isinstance(result, dict) and "renamed" in result:
                            renamed_files = result["renamed"]
                            self.log(f"成功重命名 {len(renamed_files)} 个文件")

                            # 移动文件
                            moved_count = 0
                            skipped_count = 0
                            import shutil
                            total_files = len(renamed_files)
                            for i, new_path in enumerate(renamed_files, 1):
                                try:
                                    # 确保文件存在
                                    if os.path.exists(new_path):
                                        # 从完整路径中提取文件名
                                        new_name = os.path.basename(new_path)
                                        dest_path = os.path.join(target_path, new_name)

                                        # 检查目标文件是否存在（去重）
                                        if not os.path.exists(dest_path):
                                            shutil.move(new_path, dest_path)
                                            moved_count += 1
                                            self.log(f"移动中... {i}/{total_files}")
                                        else:
                                            self.log(f"文件已存在，跳过: {new_name}")
                                            skipped_count += 1
                                except Exception as e:
                                    self.log(f"移动失败: {str(e)}", "error")

                            self.log(f"成功移动 {moved_count} 个文件到 {target_path}")
                            if skipped_count > 0:
                                self.log(f"跳过 {skipped_count} 个已存在的文件")
                        else:
                            self.log("重命名结果格式不正确", "error")
                    except Exception as e:
                        self.log(f"重命名和移动失败: {str(e)}", "error")

            self.log("\n批量自动化处理完成！")
            self.main_window.update_status("处理完成", "success")
        except Exception as e:
            self.log(f"处理失败: {str(e)}", "error")
            self.main_window.update_status("处理失败", "error")

    def _preview_process(self):
        """预览处理"""
        source_dir = self.source_dir.get().strip()
        target_dir = self.target_dir.get().strip()

        if not source_dir:
            messagebox.showwarning("警告", "请选择源文件夹")
            return

        if not target_dir:
            messagebox.showwarning("警告", "请选择目标文件夹")
            return

        if not os.path.exists(source_dir):
            messagebox.showerror("错误", f"源文件夹不存在: {source_dir}")
            return

        # 预览处理
        self.log("开始预览处理...")
        self.log(f"源目录: {source_dir}")
        self.log(f"目标目录: {target_dir}")

        try:
            # 遍历源目录下的所有子文件夹
            for item in os.listdir(source_dir):
                source_path = os.path.join(source_dir, item)
                if os.path.isdir(source_path):
                    target_path = self._get_target_folder(item)
                    self.log(f"\n预览文件夹: {item}")
                    self.log(f"目标文件夹: {target_path}")

                    # 预览去重
                    self.log("预览去重...")
                    try:
                        duplicate_count, preview_details = preview_duplicates(source_path, method="hash", recursive=False)
                        self.log(f"发现 {duplicate_count} 个重复文件")
                        for detail in preview_details:
                            if "将删除" in detail:
                                self.log(detail)
                    except Exception as e:
                        self.log(f"预览去重失败: {str(e)}", "error")

                    # 预览文件数量
                    files = []
                    for file in os.listdir(source_path):
                        file_path = os.path.join(source_path, file)
                        if os.path.isfile(file_path):
                            files.append(file)
                    self.log(f"文件夹中有 {len(files)} 个文件")

            self.log("\n预览完成！")
            self.main_window.update_status("预览完成", "success")
        except Exception as e:
            self.log(f"预览失败: {str(e)}", "error")
            self.main_window.update_status("预览失败", "error")

    def log(self, message, type="info"):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        # 在GUI中显示日志
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)

        # 使用logger记录日志
        if type == "info":
            logger.info(message)
        elif type == "success":
            logger.info(message)
        elif type == "warning":
            logger.warning(message)
        elif type == "error":
            logger.error(message)

        # 更新状态栏
        self.main_window.update_status(message, type)
