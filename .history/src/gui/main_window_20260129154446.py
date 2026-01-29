"""主窗口模块"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from src.gui.components import (
    FolderCreatorPanel,
    FileRenamerPanel,
    DuplicateRemoverPanel,
    ExcelExporterPanel,
    FolderInfoPanel
)


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        """
        初始化主窗口
        :param root: tkinter根窗口
        """
        self.root = root
        self.root.title("AI文件管理工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置窗口图标
        # self.root.iconbitmap("icon.ico")
        
        # 设置主题色
        self.theme = {
            "primary": "#4CAF50",
            "secondary": "#2196F3",
            "accent": "#FF9800",
            "background": "#f5f5f5",
            "foreground": "#333333",
            "light": "#ffffff",
            "dark": "#263238",
            "success": "#4CAF50",
            "warning": "#FFC107",
            "error": "#F44336"
        }
        
        # 设置窗口背景
        self.root.configure(bg=self.theme["background"])
        
        # 创建主容器
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建标题
        self._create_title()
        
        # 创建选项卡
        self._create_notebook()
        
        # 创建状态栏
        self._create_status_bar()
        
    def _create_title(self):
        """创建标题"""
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="AI文件管理工具",
            font=("Microsoft YaHei", 24, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        version_label = ttk.Label(
            title_frame,
            text="v1.0.0",
            font=("Microsoft YaHei", 12, "italic"),
            foreground="#666666"
        )
        version_label.pack(side=tk.RIGHT, padx=10)
    
    def _create_notebook(self):
        """创建选项卡"""
        # 创建选项卡控件
        self.notebook = ttk.Notebook(self.main_frame, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个功能面板
        self.folder_creator_panel = FolderCreatorPanel(self.notebook, self)
        self.file_renamer_panel = FileRenamerPanel(self.notebook, self)
        self.duplicate_remover_panel = DuplicateRemoverPanel(self.notebook, self)
        self.excel_exporter_panel = ExcelExporterPanel(self.notebook, self)
        self.folder_info_panel = FolderInfoPanel(self.notebook, self)
        
        # 添加选项卡
        self.notebook.add(self.folder_creator_panel, text="📁 文件夹创建")
        self.notebook.add(self.file_renamer_panel, text="✏️ 文件重命名")
        self.notebook.add(self.duplicate_remover_panel, text="🗑️ 文件去重")
        self.notebook.add(self.excel_exporter_panel, text="📊 Excel导出")
        self.notebook.add(self.folder_info_panel, text="📋 文件夹信息")
        
        # 设置选项卡样式
        style = ttk.Style()
        # 重置样式，使用更简单的设置确保文字可见
        style.configure("TNotebook", background=self.theme["background"])
        style.configure("TNotebook.Tab", 
                       background="#ffffff",
                       foreground="#000000",
                       padding=[15, 8],
                       font=("SimHei", 11))
        style.map("TNotebook.Tab", 
                  background=[("selected", "#4CAF50")],
                  foreground=[("selected", "#ffffff")])
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ttk.Frame(self.root, height=30, style="StatusBar.TFrame")
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="就绪",
            font=("Microsoft YaHei", 10),
            foreground="#666666"
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 设置状态栏样式
        style = ttk.Style()
        style.configure("StatusBar.TFrame", background=self.theme["light"])
    
    def update_status(self, message, type="info"):
        """
        更新状态栏消息
        :param message: 消息内容
        :param type: 消息类型 (info, success, warning, error)
        """
        self.status_label.config(text=message)
        
        # 根据类型设置颜色
        if type == "success":
            self.status_label.config(foreground=self.theme["success"])
        elif type == "warning":
            self.status_label.config(foreground=self.theme["warning"])
        elif type == "error":
            self.status_label.config(foreground=self.theme["error"])
        else:
            self.status_label.config(foreground="#666666")
    
    def show_message(self, title, message, type="info"):
        """
        显示消息框
        :param title: 标题
        :param message: 消息内容
        :param type: 消息类型 (info, success, warning, error)
        """
        if type == "success":
            messagebox.showinfo(title, message)
        elif type == "warning":
            messagebox.showwarning(title, message)
        elif type == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)


def run_gui():
    """
    运行GUI
    """
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
