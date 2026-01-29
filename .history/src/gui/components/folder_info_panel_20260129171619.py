    def _create_widgets(self):
        """创建控件"""
        # 头部信息
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 8))

        # 恢复标题
        ttk.Label(header_frame, text="📋 文件夹信息分析", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(header_frame, text="批量分析文件夹内所有文件的详细信息，支持导出为TXT和CSV格式",
                 font=("Microsoft YaHei", 8), foreground="#666666").pack(anchor=tk.W, pady=(3, 0))

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