"""文件夹信息面板"""
import tkinter as tk
from tkinter import ttk, filedialog


class FolderInfoPanel(ttk.Frame):
    """文件夹信息面板"""
    
    def __init__(self, parent, main_app):
        """
        初始化文件夹信息面板
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
        
        # 递归选项
        option_frame = ttk.Frame(self)
        option_frame.pack(fill=tk.X, pady=10)
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(option_frame, text="递归子文件夹", variable=self.recursive_var).pack(side=tk.LEFT, padx=5)
        
        # 分析结果
        result_frame = ttk.Frame(self)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(result_frame, text="分析结果:", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        self.result_text = tk.Text(result_frame, height=12, width=60, font=("Courier New", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # 提示标签
        ttk.Label(self, text="提示: 分析大型文件夹可能需要一些时间", font=("Microsoft YaHei", 9), foreground="#666666").pack(anchor=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="分析", command=self._analyze_folder, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self._clear_fields).pack(side=tk.LEFT, padx=5)
    
    def _browse_folder(self):
        """浏览文件夹"""
        path = filedialog.askdirectory(title="选择文件夹", initialdir=self.folder_path_var.get() or ".")
        if path:
            self.folder_path_var.set(path)
    
    def _analyze_folder(self):
        """分析文件夹"""
        folder_path = self.folder_path_var.get().strip()
        recursive = self.recursive_var.get()
        
        if not folder_path:
            self.main_app.show_message("错误", "请选择文件夹", "error")
            return
        
        try:
            from src.core.folder_info import analyze_folder_structure
            result = analyze_folder_structure(folder_path, output_format="text")
            
            # 显示结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            
            self.main_app.update_status("文件夹分析完成")
        except Exception as e:
            self.main_app.show_message("错误", f"分析失败: {str(e)}", "error")
    
    def _clear_fields(self):
        """清空输入"""
        self.folder_path_var.set("")
        self.recursive_var.set(True)
        self.result_text.delete(1.0, tk.END)
