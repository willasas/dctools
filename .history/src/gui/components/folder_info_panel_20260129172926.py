"""文件夹信息面板"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime

# 尝试导入tkinterdnd2
use_tkinterdnd = False
try:
    from tkinterdnd2 import DND_FILES
    use_tkinterdnd = True
    print("folder_info_panel: tkinterdnd2 库可用")
except ImportError:
    print("folder_info_panel: tkinterdnd2 库不可用")


class FolderInfoPanel(ttk.Frame):
    """文件夹信息面板"""

    def __init__(self, parent, main_app):
        """
        初始化文件夹信息面板
        :param parent: 父控件
        :param main_app: 主应用实例
        """
        super().__init__(parent, padding=15)
        self.main_app = main_app
        self.folder_paths = []

        self._create_widgets()
        self._setup_drag_drop()

    def _create_widgets(self):
        """创建控件"""
        # 头部信息
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 8))

        # 文件夹列表
        folder_frame = ttk.LabelFrame(self, text="文件夹列表", padding=6)
        folder_frame.pack(fill=tk.X, pady=6)

        # 减小列表高度
        self.folder_listbox = tk.Listbox(folder_frame, height=4, width=50, font=("Microsoft YaHei", 9),
                                         selectmode=tk.EXTENDED, bg="#ffffff")
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        scrollbar = ttk.Scrollbar(folder_frame, orient=tk.VERTICAL, command=self.folder_listbox.yview)
        self.folder_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 文件夹操作按钮
        button_frame = ttk.Frame(folder_frame)
        button_frame.pack(fill=tk.X, pady=(6, 0))

        # 减小按钮大小
        ttk.Button(button_frame, text="+ 添加", command=self._browse_folders, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="- 移除", command=self._remove_selected, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="清空", command=self._clear_folders, width=6).pack(side=tk.LEFT, padx=2)

        # 提示信息
        hint_frame = ttk.Frame(folder_frame)
        hint_frame.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(hint_frame, text="💡 提示: 使用添加按钮添加要分析的文件夹",
                 font=("Microsoft YaHei", 7), foreground="#888888").pack(anchor=tk.W)

        # 选项设置
        option_frame = ttk.Frame(self)
        option_frame.pack(fill=tk.X, pady=6)

        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="递归子文件夹", variable=self.recursive_var).pack(side=tk.LEFT, padx=4)

        # 导出格式
        output_frame = ttk.LabelFrame(self, text="导出格式", padding=6)
        output_frame.pack(fill=tk.X, pady=6)

        self.export_format_var = tk.StringVar(value="txt")
        ttk.Radiobutton(output_frame, text="TXT (阅读)", variable=self.export_format_var,
                       value="txt").pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(output_frame, text="CSV (Excel)", variable=self.export_format_var,
                       value="csv").pack(side=tk.LEFT, padx=6)

        # 进度显示
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, pady=6)

        self.progress_var = tk.StringVar(value="就绪")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var,
                                        font=('Microsoft YaHei', 8))
        self.progress_label.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=100)
        self.progress_bar.pack(fill=tk.X, pady=(2, 0))

        # 结果预览
        result_frame = ttk.LabelFrame(self, text="分析结果", padding=6)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        # 减小文本框高度
        self.result_text = tk.Text(result_frame, height=5, width=50, font=('Courier New', 8),
                                   bg="#f5f5f5", state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 主操作按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=6)

        # 减小按钮大小
        ttk.Button(button_frame, text="📊 分析", command=self._analyze_folders,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📤 导出", command=self._analyze_folders).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="📁 快速", command=self._quick_analyze).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="清空", command=self._clear_all).pack(side=tk.RIGHT, padx=2)

    def _setup_drag_drop(self):
        """设置拖放支持"""
        if use_tkinterdnd:
            try:
                # 使用tkinterdnd2设置拖放功能
                print("尝试使用tkinterdnd2设置拖放功能")

                # 为当前面板注册拖放目标
                if hasattr(self, 'drop_target_register'):
                    self.drop_target_register(DND_FILES)
                    self.dnd_bind('<<Drop>>', self._on_drop)
                    print("拖放功能设置成功")
                else:
                    print("当前组件不支持拖放注册")

            except Exception as e:
                # 拖放功能设置失败时静默失败
                print(f"拖放功能设置失败: {str(e)}")
                pass
        else:
            print("tkinterdnd2 不可用，无法启用拖拽功能")
            print("请使用添加文件夹按钮来添加要分析的文件夹")

    def _on_drag_enter(self, event):
        """鼠标拖拽进入窗口"""
        print("鼠标拖拽进入窗口")
        # 可以添加视觉反馈
        pass

    def _on_drag_leave(self, event):
        """鼠标拖拽离开窗口"""
        print("鼠标拖拽离开窗口")
        # 可以移除视觉反馈
        pass

    def _on_drop(self, event):
        """处理拖放事件"""
        try:
            print("接收到拖放事件")

            # 检查事件是否包含数据
            if hasattr(event, 'data'):
                data = event.data
                print(f"拖放数据: {data}")

                if data:
                    # 尝试使用win32api解析拖放数据
                    try:
                        import win32api
                        files = win32api.ParseCommandLine(data)
                        print(f"解析到文件: {files}")
                    except ImportError:
                        # 如果没有win32api，使用简单的字符串处理
                        files = [data.strip('"')]
                        print(f"简单解析: {files}")

                    for file_path in files:
                        file_path = file_path.strip('"')
                        print(f"处理文件路径: {file_path}")
                        if os.path.isdir(file_path):
                            if file_path not in self.folder_paths:
                                self.folder_paths.append(file_path)
                                self.folder_listbox.insert(tk.END, file_path)
                                if hasattr(self, 'main_app'):
                                    self.main_app.update_status(f"已添加文件夹: {os.path.basename(file_path)}")
                                print(f"成功添加文件夹: {file_path}")
        except Exception as e:
            # 拖放处理失败时静默失败
            print(f"拖放处理失败: {str(e)}")
            pass

    def _browse_folders(self):
        """浏览选择多个文件夹"""
        paths = filedialog.askdirectory(title="选择文件夹", initialdir=".", mustexist=True)
        if paths:
            if paths not in self.folder_paths:
                self.folder_paths.append(paths)
                self.folder_listbox.insert(tk.END, paths)
                self.main_app.update_status(f"已添加文件夹: {os.path.basename(paths)}")

    def _browse_folder(self):
        """浏览选择单个文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=".", mustexist=True)
        if path:
            if path not in self.folder_paths:
                self.folder_paths.append(path)
                self.folder_listbox.insert(tk.END, path)
            # 注意：folder_path_var 可能不存在，这里做了注释
            # self.folder_path_var.set(path)

    def _remove_selected(self):
        """移除选中的文件夹"""
        selected = self.folder_listbox.curselection()
        if selected:
            for index in reversed(selected):
                path = self.folder_paths.pop(index)
                self.folder_listbox.delete(index)
                self.main_app.update_status(f"已移除: {os.path.basename(path)}")

    def _clear_folders(self):
        """清空文件夹列表"""
        self.folder_paths = []
        self.folder_listbox.delete(0, tk.END)
        self.main_app.update_status("已清空文件夹列表")

    def _analyze_folders(self):
        """分析文件夹"""
        if not self.folder_paths:
            self.main_app.show_message("提示", "请先添加要分析的文件夹", "info")
            return

        recursive = self.recursive_var.get()
        export_format = self.export_format_var.get()

        try:
            self.progress_var.set("正在分析文件夹...")

            from src.core.folder_info import export_to_txt, export_to_csv

            total_folders = len(self.folder_paths)

            for i, folder_path in enumerate(self.folder_paths):
                folder_name = os.path.basename(folder_path)
                self.progress_var.set(f"正在分析: {folder_name} ({i+1}/{total_folders})")
                self.progress_bar['value'] = (i / total_folders) * 100
                # 移除root.update()调用，避免可能的错误

            if export_format == "txt":
                output_path = export_to_txt(self.folder_paths, recursive=recursive)
            else:
                output_path = export_to_csv(self.folder_paths, recursive=recursive)

            self.progress_var.set(f"分析完成！结果已保存到: {output_path}")
            self.progress_bar['value'] = 100

            result_text = f"✅ 分析完成！\n\n输出文件: {output_path}\n分析文件夹数: {len(self.folder_paths)}\n递归模式: {'是' if recursive else '否'}\n导出格式: {'TXT' if export_format == 'txt' else 'CSV'}"

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            self.result_text.config(state=tk.DISABLED)

            self.main_app.update_status(f"文件分析完成，共处理 {len(self.folder_paths)} 个文件夹")

            if messagebox.askyesno("分析完成", f"分析结果已保存到:\n{output_path}\n\n是否打开文件？"):
                os.startfile(output_path)

        except Exception as e:
            self.progress_var.set(f"分析失败: {str(e)}")
            self.main_app.show_message("错误", f"分析失败: {str(e)}", "error")

    def _quick_analyze(self):
        """快速分析文件夹结构"""
        if not self.folder_paths:
            self.main_app.show_message("提示", "请先添加要分析的文件夹", "info")
            return

        try:
            from src.core.folder_info import analyze_folder_structure

            results = []
            for folder_path in self.folder_paths:
                result = analyze_folder_structure(folder_path, output_format="text")
                results.append(f"\n{'='*50}\n")
                results.append(result)

            full_result = "".join(results)

            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, full_result)
            self.result_text.config(state=tk.DISABLED)

            self.main_app.update_status("快速分析完成")

        except Exception as e:
            self.main_app.show_message("错误", f"分析失败: {str(e)}", "error")

    def _clear_all(self):
        """清空所有"""
        self._clear_folders()
        self.recursive_var.set(True)
        self.export_format_var.set("txt")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.progress_var.set("就绪")
        self.progress_bar['value'] = 0
