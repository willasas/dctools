"""批量自动化面板"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time
import queue
import re
import shutil

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
                    "梦千秋": "M_梦千秋",
                    "丁雪": "D_丁雪",
                    "东凰太心": "D_东凰太心",
                    "东方凤凰": "D_东方凤凰",
                    "丰川祥子": "F_丰川祥子",
                    "云悠悠": "Y_云悠悠",
                    "云曦": "Y_云曦",
                    "云曦1": "Y_云曦",
                    "云曦2": "Y_云曦",
                    "云曦3": "Y_云曦",
                    "云望舒": "Y_云望舒",
                    "云霄": "Y_云霄",
                    "云霄2": "Y_云霄",
                    "云韵": "Y_云韵",
                    "云韵2": "Y_云韵",
                    "付馨允": "F_付馨允",
                    "优菈2": "Y_优菈",
                    "信浓": "X_信浓",
                    "元瑶": "Y_元瑶",
                    "光明女神": "G_光明女神",
                    "兴登堡": "X_兴登堡",
                    "兹白": "Z_兹白",
                    "内丽莎": "N_内丽莎",
                    "冷筱": "L_冷筱",
                    "凝光": "N_凝光",
                    "剑妈": "J_剑妈",
                    "剑妈1": "J_剑妈",
                    "剑妈2": "J_剑妈",
                    "勘解由小路": "K_勘解由小路",
                    "千木": "Q_千木",
                    "南小橙": "N_南小橙",
                    "南水水": "N_南水水",
                    "南水水2": "N_南水水",
                    "南簪": "N_南簪",
                    "卡芙卡": "K_卡芙卡",
                    "卢西娅": "L_卢西娅",
                    "原创": "Y_原创",
                    "原创1": "Y_原创",
                    "原创2": "Y_原创",
                    "古薰儿": "G_古薰儿",
                    "古薰儿2": "G_古薰儿",
                    "叶倾仙": "Y_叶倾仙",
                    "叶夕水": "Y_叶夕水",
                    "叶紫芸": "Y_叶紫芸",
                    "叶骨衣": "Y_叶骨衣",
                    "司幼幽": "S_司幼幽",
                    "吟霖": "Y_吟霖",
                    "吴懿": "W_吴懿",
                    "吴茵": "W_吴茵",
                    "吾妻": "W_吾妻",
                    "哥伦比娅": "G_哥伦比娅",
                    "唐月华": "T_唐月华",
                    "唐舞桐": "T_唐舞桐",
                    "四叶真夜": "S_四叶真夜",
                    "圣路易斯": "S_圣路易斯",
                    "圣采儿": "S_圣采儿",
                    "圣采儿2": "S_圣采儿",
                    "圣采儿3": "S_圣采儿",
                    "坎特蕾拉": "K_坎特蕾拉",
                    "多角色玉足": "D_多角色玉足",
                    "天狐仙子": "T_天狐仙子",
                    "天穹长老": "T_天穹",
                    "姜立": "J_姜立",
                    "姬凝霜": "J_姬凝霜",
                    "姬如雪": "J_姬如雪",
                    "姬紫月": "J_姬紫月",
                    "姬青": "J_姬青",
                    "姮娥": "H_姮娥",
                    "娘娘": "N_娘娘",
                    "宁雨蝶": "N_宁雨蝶",
                    "守岸人": "S_守岸人",
                    "宋玉": "S_宋玉",
                    "宋玉1": "S_宋玉",
                    "宋玉2": "S_宋玉",
                    "封念云": "F_封念云",
                    "封念云2": "F_封念云",
                    "小医仙": "X_小医仙",
                    "小医仙1": "X_小医仙",
                    "小美人鱼": "X_小美人鱼",
                    "小舞": "X_小舞",
                    "小舞1": "X_小舞",
                    "小舞2": "X_小舞",
                    "小舞3": "X_小舞",
                    "小青": "X_小青",
                    "尤菈": "Y_尤菈",
                    "布洛妮娅": "B_布洛妮娅",
                    "希诺宁": "X_希诺宁",
                    "建武": "J_建武",
                    "弩S": "N_弩S",
                    "徐欣": "X_徐欣",
                    "徐欣2": "X_徐欣",
                    "怨仇": "Y_怨仇",
                    "拉克丝": "L_拉克丝",
                    "文思月": "W_文思月",
                    "新泽西": "X_新泽西",
                    "方清雪": "F_方清雪",
                    "易文君": "Y_易文君",
                    "昔链": "X_昔链",
                    "星幻王": "X_星幻王",
                    "星幻王1": "X_星幻王",
                    "星见雅": "X_星见雅",
                    "曹颖": "C_曹颖",
                    "曹颖1": "C_曹颖",
                    "曹颖2": "C_曹颖",
                    "有琴玄雅": "Y_有琴玄雅",
                    "朱竹清": "Z_朱竹清",
                    "李慕婉": "L_李慕婉",
                    "柳七月": "L_柳七月",
                    "柳玉": "L_柳玉",
                    "柳玉2": "L_柳玉",
                    "柳玉3": "L_柳玉",
                    "柳眉": "L_柳眉",
                    "桃乐丝": "T_桃乐丝",
                    "梅凝": "M_梅凝",
                    "梦可儿": "M_梦可儿",
                    "梦可儿2": "M_梦可儿",
                    "楚萱儿": "C_楚萱儿",
                    "楚萱儿2": "C_楚萱儿",
                    "橘子": "J_橘子",
                    "欧根亲王": "O_欧根亲王",
                    "武藏": "W_武藏",
                    "汉库克": "H_汉库克",
                    "江楠楠": "J_江楠楠",
                    "洛璃": "L_洛璃",
                    "洛璃2": "L_洛璃",
                    "流萤": "L_流萤",
                    "海瑟音": "H_海瑟音",
                    "清漪": "Q_清漪",
                    "渡边加奈子": "D_渡边加奈子",
                    "溟莲之主": "M_溟莲之主",
                    "溪幼琴": "X_溪幼琴",
                    "溪幼琴1": "X_溪幼琴",
                    "火允儿": "H_火允儿",
                    "火允儿1": "H_火允儿",
                    "火灵儿": "H_火灵儿",
                    "火灵儿2": "H_火灵儿",
                    "灵毓秀": "L_灵毓秀",
                    "炽阳华明": "C_炽阳华明",
                    "焰灵姬": "Y_焰灵姬",
                    "燕倾菲": "Y_燕倾菲",
                    "燕如嫣": "Y_燕如嫣",
                    "爱宕": "A_爱宕",
                    "爱弥斯": "A_爱弥斯",
                    "爻光": "Y_爻光",
                    "独孤雁": "D_独孤雁",
                    "玄衣": "X_玄衣",
                    "玄衣1": "X_玄衣",
                    "玄衣2": "X_玄衣",
                    "王琳": "W_王琳",
                    "王秋儿": "W_王秋儿",
                    "王秋儿2": "W_王秋儿",
                    "王秋儿3": "W_王秋儿",
                    "玛律恰那": "M_玛律恰那",
                    "琳奈": "L_琳奈",
                    "瑶池圣女": "Y_瑶池圣女",
                    "甘璇": "G_甘璇",
                    "白月蓉": "B_白月蓉",
                    "白雪": "B_白雪",
                    "白龙": "B_白龙",
                    "碧蓝航线": "B_碧蓝航线",
                    "神里绫华": "S_神里绫华",
                    "秘书": "M_秘书",
                    "穆婉清": "M_穆婉清",
                    "穆碗清": "M_穆碗清",
                    "紫妍": "Z_紫妍",
                    "紫灵": "Z_紫灵",
                    "紫灵2": "Z_紫灵",
                    "紫灵3": "Z_紫灵",
                    "紫灵4": "Z_紫灵",
                    "紫萱": "Z_紫萱",
                    "胡妙": "H_胡妙",
                    "胡滕": "H_胡滕",
                    "芙宁娜": "F_芙宁娜",
                    "芙露德莉斯": "F_芙露德莉斯",
                    "莫斯科": "M_莫斯科",
                    "莫雨": "M_莫雨",
                    "萧潇": "X_萧潇",
                    "萧潇2": "X_萧潇",
                    "萧潇3": "X_萧潇",
                    "蒂法": "D_蒂法",
                    "蓝梦": "L_蓝梦",
                    "蔷薇": "Q_蔷薇",
                    "虞渊初雨": "Y_虞渊初雨",
                    "蚩梦": "C_蚩梦",
                    "调月莉音": "D_调月莉音",
                    "调月莉音2": "D_调月莉音",
                    "貂蝉": "D_貂蝉",
                    "贝拉": "B_贝拉",
                    "赞妮": "Z_赞妮",
                    "远坂凛": "Y_远坂凛",
                    "迪盖特鲁因": "D_迪盖特鲁因",
                    "邀月": "Y_邀月",
                    "邪花侯": "X_邪花侯",
                    "金小钗": "J_金小钗",
                    "金瓶儿": "J_金瓶儿",
                    "银月1": "Y_银月",
                    "银狼": "Y_银狼",
                    "银环": "Y_银环",
                    "镜流": "J_镜流",
                    "长夜月": "C_长夜月",
                    "长离": "Z_长离",
                    "阿尔图罗": "A_阿尔图罗",
                    "阿尔法": "A_阿尔法",
                    "阿格莱雅": "A_阿格莱雅",
                    "阿格莱雅2": "A_阿格莱雅",
                    "阿狸": "A_阿狸",
                    "阿蕾奇诺": "A_阿蕾奇诺",
                    "阿银": "A_阿银",
                    "陆嫁嫁": "L_陆嫁嫁",
                    "陆雪琪": "L_陆雪琪",
                    "陆雪琪2": "L_陆雪琪",
                    "雅儿贝德": "Y_雅儿贝德",
                    "雉圭": "Z_雉圭",
                    "雉圭2": "Z_雉圭",
                    "雨馨": "Y_雨馨",
                    "雨馨1": "Y_雨馨",
                    "雪帝": "X_雪帝",
                    "雪帝1": "X_雪帝",
                    "雪帝2": "X_雪帝",
                    "雷电将军": "L_雷电将军",
                    "青仙子": "Q_青仙子",
                    "青仙子2": "Q_青仙子",
                    "青仙子3": "Q_青仙子",
                    "青玉": "Q_青玉",
                    "马小桃": "M_马小桃",
                    "齐琪": "Q_齐琪",
                    "龙娇男": "L_龙娇男",
                    "龙娇男2": "L_龙娇男",
                    "十三姨": "S_十三姨",
                    "将臣": "J_将臣",
                    "尸魈": "S_尸魈",
                    "楚宣儿": "C_楚宣儿",
                    "三水": "S_三水",
                    "上官玉儿": "S_上官玉儿",
                    "不知火舞": "B_不知火舞",
                    "不闻不问": "B_不闻不问",
                    "东方淮竹": "D_东方淮竹",
                    "丝柯克": "S_丝柯克",
                    "丹晨": "D_丹晨",
                    "丽莎": "L_丽莎",
                    "九幽雀": "J_九幽雀",
                    "云落": "Y_云落",
                    "人造人十八号": "R_人造人十八号",
                    "仙子": "X_仙子",
                    "仙清儿": "X_仙清儿",
                    "仙琴之主": "X_仙琴之主",
                    "仙遗三祖": "X_仙遗三祖",
                    "伊琳娜": "Y_伊琳娜",
                    "伊芙琳": "Y_伊芙琳",
                    "伊轻舞": "Y_伊轻舞",
                    "健身女孩": "J_健身女孩",
                    "僰人古巫": "B_僰人古巫",
                    "兔女郎": "T_兔女郎",
                    "公孙杏": "G_公孙杏",
                    "公孙离": "G_公孙离",
                    "兽耳娘": "S_兽耳娘",
                    "写实": "X_写实",
                    "冰天雪女": "B_冰天雪女",
                    "冰帝": "B_冰帝",
                    "凌玉灵": "L_凌玉灵",
                    "凌落宸": "L_凌落宸",
                    "凤凰": "F_凤凰",
                    "凤栾": "F_凤栾",
                    "凤清儿": "F_凤清儿",
                    "凭依身": "P_凭依身",
                    "凯莎": "K_凯莎",
                    "凰女": "H_凰女",
                    "则天女帝": "Z_则天女帝",
                    "千仞雪": "Q_千仞雪",
                    "南冥玉漱": "N_南冥玉漱",
                    "南宫仙儿": "N_南宫仙儿",
                    "南宫夕儿": "N_南宫夕儿",
                    "南宫婉": "N_南宫婉",
                    "南秋秋": "N_南秋秋",
                    "卡丹": "K_卡丹",
                    "即墨花雪": "J_即墨花雪",
                    "古佩儿": "G_古佩儿",
                    "叶婵宫": "Y_叶婵宫",
                    "叶嫣然": "Y_叶嫣然",
                    "叶欣蓝": "Y_叶欣蓝",
                    "叶泠泠": "Y_叶泠泠",
                    "叶浅静": "Y_叶浅静",
                    "叶若依": "Y_叶若依",
                    "叶轻语": "Y_叶轻语",
                    "司妙玲": "S_司妙玲",
                    "司芸香": "S_司芸香",
                    "吕清儿": "L_吕清儿",
                    "吕虹": "L_吕虹",
                    "周漪": "Z_周漪",
                    "周紫虹": "Z_周紫虹",
                    "唐梦儿": "T_唐梦儿",
                    "唐火儿": "T_唐火儿",
                    "唐紫尘": "T_唐紫尘",
                    "唐雅": "T_唐雅",
                    "唐雨": "T_唐雨",
                    "唐雪见": "T_唐雪见",
                    "啦啦队少女": "L_啦啦队少女",
                    "四妹": "S_四妹",
                    "国漫": "G_国漫",
                    "圣域龙灵": "S_圣域龙灵",
                    "圣女": "S_圣女",
                    "圣莲": "S_圣莲",
                    "圣诞": "S_圣诞",
                    "地狱吹雪": "D_地狱吹雪",
                    "夏禾": "X_夏禾",
                    "夜小泪": "Y_夜小泪",
                    "大乔": "D_大乔",
                    "大娘": "D_大娘",
                    "大腚": "D_大腚",
                    "大骊皇后": "D_大骊皇后",
                    "天使圣王": "T_天使圣王",
                    "天女兽": "T_天女兽",
                    "天女蕊": "T_天女蕊",
                    "天妖傀": "T_天妖傀",
                    "天瑶": "T_天瑶",
                    "天穹": "T_天穹",
                    "太阴玉兔": "T_太阴玉兔",
                    "夭夜公主": "Y_夭夜公主",
                    "奉眠": "F_奉眠",
                    "奥姑": "A_奥姑",
                    "奥杜因": "A_奥杜因",
                    "女剑侍": "N_女剑侍",
                    "女帝": "N_女帝",
                    "女律师": "N_女律师",
                    "女战神": "N_女战神",
                    "妖刀姬": "Y_妖刀姬",
                    "妖夜": "Y_妖夜",
                    "妖娆": "Y_妖娆",
                    "妙妙公主": "M_妙妙公主",
                    "妮姬": "N_妮姬",
                    "姚坊主": "Y_姚坊主",
                    "姜澜": "J_姜澜",
                    "姜雀": "J_姜雀",
                    "姬如月": "J_姬如月",
                    "姬小满": "J_姬小满",
                    "婷儿": "T_婷儿",
                    "孙尚香": "S_孙尚香",
                    "孟仙姑": "M_孟仙姑",
                    "季莹莹": "J_季莹莹",
                    "孤月剑仙": "G_孤月剑仙",
                    "宁姚": "N_宁姚",
                    "宁红叶": "N_宁红叶",
                    "宁荣荣": "N_宁荣荣",
                    "宋嫣": "S_宋嫣",
                    "宝青坊主": "B_宝青坊主",
                    "小月婵": "X_小月婵",
                    "小樱": "X_小樱",
                    "小狸": "X_小狸",
                    "小雪城主夫人": "X_小雪城主夫人",
                    "小麋鹿": "X_小麋鹿",
                    "小龙女": "X_小龙女",
                    "少司命": "S_少司命",
                    "巫风": "W_巫风",
                    "巴巴塔": "B_巴巴塔",
                    "布洛琳": "B_布洛琳",
                    "布雷斯特": "B_布雷斯特",
                    "师姐": "S_师姐",
                    "席拉": "X_席拉",
                    "幽兰黛尔": "Y_幽兰黛尔",
                    "幽月": "Y_幽月",
                    "应月茹": "Y_应月茹",
                    "张小凡": "Z_张小凡",
                    "彦": "Y_彦",
                    "忘归人": "W_忘归人",
                    "念奴娇": "N_念奴娇",
                    "性感": "X_性感",
                    "情魔神": "Q_情魔神",
                    "想入菲菲": "X_想入菲菲",
                    "慕沛灵": "M_慕沛灵",
                    "慕青鸾": "M_慕青鸾",
                    "手榴弹": "S_手榴弹",
                    "手绘": "S_手绘",
                    "护士": "H_护士",
                    "搜查官": "S_搜查官",
                    "敖乙": "A_敖乙",
                    "敖闰": "A_敖闰",
                    "教师": "J_教师",
                    "斗罗小白": "D_斗罗小白",
                    "明日香": "M_明日香",
                    "明珠夫人": "M_明珠夫人",
                    "昔涟": "X_昔涟",
                    "星野": "X_星野",
                    "春日野穹": "C_春日野穹",
                    "晏琉璃": "Y_晏琉璃",
                    "晓月": "X_晓月",
                    "晓梦": "X_晓梦",
                    "曹敬观音": "C_曹敬观音",
                    "月夜公主": "Y_月夜公主",
                    "月姬": "Y_月姬",
                    "木仙": "M_木仙",
                    "朱露": "Z_朱露",
                    "朽叶千咲": "X_朽叶千咲",
                    "李宝瓶": "L_李宝瓶",
                    "李寒衣": "L_李寒衣",
                    "李小曼": "L_李小曼",
                    "李少英": "L_李少英",
                    "李长寿": "L_李长寿",
                    "杨玉环": "Y_杨玉环",
                    "林秀": "L_林秀",
                    "林紫玥": "L_林紫玥",
                    "林青檀": "L_林青檀",
                    "枫玲儿": "F_枫玲儿",
                    "柳二龙": "L_柳二龙",
                    "柳如烟": "L_柳如烟",
                    "柳妃": "L_柳妃",
                    "柳情": "L_柳情",
                    "柳菲": "L_柳菲",
                    "桂乃芬": "G_桂乃芬",
                    "梅大夫": "M_梅大夫",
                    "梅妃": "M_梅妃",
                    "梅杜莎": "M_梅杜莎",
                    "梦羽衣": "M_梦羽衣",
                    "楚月婵": "C_楚月婵",
                    "楚灵儿": "C_楚灵儿",
                    "樊巧儿": "F_樊巧儿",
                    "横屏壁纸": "H_横屏壁纸",
                    "步练师": "B_步练师",
                    "毒血夫人": "D_毒血夫人",
                    "比比东": "B_比比东",
                    "水冰儿": "S_水冰儿",
                    "江玉婵": "J_江玉婵",
                    "江芳": "J_江芳",
                    "汤永琴": "T_汤永琴",
                    "汪夫人": "W_汪夫人",
                    "沈燃": "S_沈燃",
                    "沙滩排球": "S_沙滩排球",
                    "沧月": "C_沧月",
                    "波利": "B_波利",
                    "波塞西": "B_波塞西",
                    "波雅·汉库克": "B_波雅·汉库克",
                    "流风霜": "L_流风霜",
                    "海琴烟": "H_海琴烟",
                    "温夫人": "W_温夫人",
                    "温洛玉": "W_温洛玉",
                    "潇潇": "X_潇潇",
                    "潜伏者": "Q_潜伏者",
                    "澹台派掌门": "T_澹台派掌门",
                    "火箭筒": "H_火箭筒",
                    "灵诺": "L_灵诺",
                    "炎姬": "Y_炎姬",
                    "炙心": "Z_炙心",
                    "炸弹": "Z_炸弹",
                    "爱宕": "A_爱宕",
                    "爱弥斯": "A_爱弥斯",
                    "爱神": "A_爱神",
                    "爱莉希雅": "A_爱莉希雅",
                    "玉娑": "Y_玉娑",
                    "玉婆婆": "Y_玉婆婆",
                    "玉贵妃": "Y_玉贵妃",
                    "王冬儿": "W_王冬儿",
                    "王林": "W_王林",
                    "王牌蛇女": "wpsn_王牌蛇女",
                    "王舞": "W_王舞",
                    "王语嫣": "W_王语嫣",
                    "玖酒": "J_玖酒",
                    "玛莉·萝丝": "M_玛莉·萝丝",
                    "玥瑶": "Y_玥瑶",
                    "玲珑": "L_玲珑",
                    "珍妮特": "Z_珍妮特",
                    "琥珀": "H_琥珀",
                    "瑜伽老师": "Y_瑜伽老师",
                    "瑶": "Y_瑶",
                    "玉陌": "Y_玉陌",
                    "申鹤": "S_申鹤",
                    "白亦君": "B_白亦君",
                    "白幽幽": "B_白幽幽",
                    "白月魁": "B_白月魁",
                    "白樱": "B_白樱",
                    "白沉香": "B_白沉香",
                    "白狐": "B_白狐",
                    "白玥": "B_白玥",
                    "白蛇": "B_白蛇",
                    "白领": "B_白领",
                    "皇莆静": "H_皇莆静",
                    "皮衣雏田": "P_皮衣雏田",
                    "真人": "Z_真人",
                    "真凰": "Z_真凰",
                    "督察官": "D_督察官",
                    "知画": "Z_知画",
                    "短发内衣": "D_短发内衣",
                    "石昊": "S_石昊",
                    "碧姬": "B_碧姬",
                    "碧游": "B_碧游",
                    "神官": "S_神官",
                    "神藤": "S_神藤",
                    "秋月华": "Q_秋月华",
                    "秦妖娆": "Q_秦妖娆",
                    "秦怡宁": "Q_秦怡宁",
                    "秦瑶": "Q_秦瑶",
                    "程灵": "C_程灵",
                    "稚圭": "Z_稚圭",
                    "空姐": "K_空姐",
                    "端木芸": "D_端木芸",
                    "笋儿": "S_笋儿",
                    "简杜": "J_简杜",
                    "精灵女骑士": "J_精灵女骑士",
                    "索拉": "S_索拉",
                    "紫女": "Z_紫女",
                    "紫霞": "Z_紫霞",
                    "红弦": "H_红弦",
                    "约尔太太": "Y_约尔太太",
                    "纲手": "G_纲手",
                    "纳兰嫣然": "N_纳兰嫣然",
                    "继M和继J Ⅱ": "J_继M和继J Ⅱ",
                    "维妮娜": "W_维妮娜",
                    "罗莎琳": "L_罗莎琳",
                    "罗莎琳·克鲁兹希卡·洛厄法特": "L_罗莎琳·克鲁兹希卡·洛厄法特",
                    "美杜莎": "M_美杜莎",
                    "聂云竹": "N_聂云竹",
                    "肖凝儿": "N_肖凝儿",
                    "胡列娜": "H_胡列娜",
                    "胡媚儿": "H_胡媚儿",
                    "胡美人": "H_胡美人",
                    "艾琳": "A_艾琳",
                    "艾辰": "A_艾辰",
                    "芮贝卡": "R_芮贝卡",
                    "花锦": "H_花锦",
                    "苏兰": "S_苏兰",
                    "苏利亚·库玛尼·安特里": "S_苏利亚·库玛尼·安特里",
                    "苏媚": "S_苏媚",
                    "苏媚瑶": "S_苏媚瑶",
                    "苏檀儿": "S_苏檀儿",
                    "苏沐": "S_苏沐",
                    "苏灵韵": "S_苏灵韵",
                    "范静梅": "F_范静梅",
                    "荷光者": "H_荷光者",
                    "莉音": "L_莉音",
                    "莫莉": "M_莫莉",
                    "莫雨馨": "M_莫雨馨",
                    "菡云芝": "H_菡云芝",
                    "萤勾": "Y_萤勾",
                    "萧媚": "X_萧媚",
                    "萧玉": "X_萧玉",
                    "落尘": "L_落尘",
                    "蓝灵娥": "L_蓝灵娥",
                    "蔡金简": "C_蔡金简",
                    "薇薇安": "W_薇薇安",
                    "藤原书记": "T_藤原书记",
                    "虞姬": "Y_虞姬",
                    "蚊道人": "W_蚊道人",
                    "蛋蛋女王": "D_蛋蛋女王",
                    "蝴蝶忍": "H_蝴蝶忍",
                    "蝶衣": "D_蝶衣",
                    "血妖女王": "X_血妖女王",
                    "袁天罡": "Y_袁天罡",
                    "西施": "X_西施",
                    "角色设定": "J_角色设定",
                    "许夫人": "X_许夫人",
                    "谭芸": "T_谭芸",
                    "赏月": "S_赏月",
                    "赵襄儿": "Z_赵襄儿",
                    "辛如音": "X_辛如音",
                    "迦南": "J_迦南",
                    "邪神": "X_邪神",
                    "金玉环": "J_金玉环",
                    "钟秀": "Z_钟秀",
                    "银凰雪琳": "Y_银凰雪琳",
                    "银雪候": "Y_银雪候",
                    "锦娘": "J_锦娘",
                    "镜": "J_镜",
                    "阎夫人": "Y_阎夫人",
                    "阮秀": "R_阮秀",
                    "阿七": "A_阿七",
                    "阿图卡": "A_阿图卡",
                    "阿尔图罗": "A_阿尔图罗",
                    "阿尔法": "A_阿尔法",
                    "阿岚": "A_阿岚",
                    "阿格莱雅": "A_阿格莱雅",
                    "阿狸": "A_阿狸",
                    "阿蕾奇诺": "A_阿蕾奇诺",
                    "阿轲": "A_阿轲",
                    "陆嘉静": "L_陆嘉静",
                    "陈樱儿": "C_陈樱儿",
                    "陈雪琪": "C_陈雪琪",
                    "降臣": "J_降臣",
                    "随风起舞": "S_随风起舞",
                    "雅妃": "Y_雅妃",
                    "雅菲": "Y_雅菲",
                    "雪女": "X_雪女",
                    "雪魅": "X_雪魅",
                    "露娜": "L_露娜",
                    "青萝": "Q_青萝",
                    "青霜": "Q_青霜",
                    "青鳞": "Q_青鳞",
                    "韩月": "H_韩月",
                    "韩湘绣": "H_韩湘绣",
                    "韩雪": "H_韩雪",
                    "须灵犀": "X_须灵犀",
                    "风秋雨": "F_风秋雨",
                    "飘渺神王": "P_飘渺神王",
                    "马兰花": "M_马兰花",
                    "高坂静流": "G_高坂静流",
                    "魄瑜侯": "P_魄瑜侯",
                    "魅女": "M_魅女",
                    "魔族妖夜": "M_魔族妖夜",
                    "鱼三娘": "Y_鱼三娘",
                    "鹤熙": "H_鹤熙",
                    "鹤童": "H_鹤童",
                    "麒麟女": "Q_麒麟女",
                    "麦朵": "M_麦朵",
                    "黑兽": "H_黑兽",
                    "龙儿": "L_龙儿",
                    "龙吉": "L_龙吉",
                    "龙宣": "L_龙宣",
                    "龙雅婷": "L_龙雅婷",
                }
                # 保存默认映射
                self._save_mapping()
        except Exception as e:
            print(f"加载映射文件失败: {str(e)}")
            self.folder_mapping = {}

        # 更新映射树视图
        self._update_mapping_tree()

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
        """根据文件夹名称获取目标文件夹

        匹配规则（按优先级）：
        1. 精确匹配 folder_name == key
        2. 带编号的文件夹 folder_name.startswith(key + "_") 或 folder_name.startswith(key + str(number))
        """
        # 首先尝试精确匹配
        if folder_name in self.folder_mapping:
            return os.path.join(self.target_dir.get(), self.folder_mapping[folder_name])

        # 然后尝试前缀匹配（处理带编号的文件夹如"云曦1"、"云曦_副本"等）
        for key, value in self.folder_mapping.items():
            # 检查 folder_name 是否以 key 开头，后面跟随下划线或数字
            if folder_name.startswith(key):
                suffix = folder_name[len(key):]
                # 如果后缀是空的或者是下划线开头的或者是数字开头的，认为是匹配
                if not suffix or suffix.startswith('_') or suffix.isdigit():
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

                            # 使用队列进行线程间通信
                            result_queue = queue.Queue()

                            def ask_delete():
                                result = messagebox.askyesno("确认", f"发现 {duplicate_count} 个重复文件，是否删除？")
                                result_queue.put(result)

                            # 在主线程中执行对话框操作
                            self.after(0, ask_delete)

                            # 等待用户响应
                            try:
                                # 最多等待60秒
                                delete_duplicates = result_queue.get(timeout=60)
                                if delete_duplicates:
                                    remove_duplicates(source_path, method="hash", recursive=False)
                                    self.log("重复文件已删除")
                                else:
                                    self.log("用户取消删除重复文件")
                            except queue.Empty:
                                # 超时，默认不删除
                                self.log("用户未响应，取消删除重复文件")
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
