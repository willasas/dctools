"""生成壁纸文件夹的映射并更新代码"""
import os
import re
from pypinyin import pinyin, Style

def get_pinyin_initial(name):
    """获取拼音首字母"""
    return ''.join([item[0][0] for item in pinyin(name, style=Style.NORMAL)])

# 目标文件夹
target_dir = r'E:\AI玲珑\壁纸'

# 当前默认映射表中的所有key（从代码中提取）
existing_keys = {
    "云望舒", "炽阳华明", "燕倾菲", "月皇", "兰若", "姚惜雪", "李慕婉", "红蝶", "赵欣梦", "魅姬",
    "雷电将军", "徐欣", "魄瑜候", "潮女妖", "焰灵姬", "云曦", "叶倾仙", "晓月仙子", "月婵", "月柳",
    "柳神", "清漪", "火灵儿", "狠人大帝", "王曦", "莫仙", "蓝仙", "虚天神藤", "邀月", "雪琳", "魔女",
    "龙女", "云霄", "女娲", "姮娥", "姜力", "姜立", "左秋琳", "穆红绫", "绫清竹", "幽千雪", "南宫锦",
    "圣采儿", "周小环", "小白", "碧瑶", "陆雪琪", "姚曦", "姬紫月", "安妙依", "瑶池圣女", "紫府圣女",
    "薇薇", "西王母", "阴阳圣女", "刘月", "燕倾城", "赵琳儿", "梦千秋", "丁雪", "东凰太心", "东方凤凰",
    "丰川祥子", "云悠悠", "云曦1", "云曦2", "云曦3", "云望舒", "云霄2", "云韵", "云韵2", "付馨允",
    "优菈2", "信浓", "元瑶", "光明女神", "兴登堡", "兹白", "内丽莎", "冷筱", "凝光", "剑妈", "剑妈1",
    "剑妈2", "勘解由小路", "千咲", "千木", "南小橙", "南水水", "南水水2", "南簪", "卡芙卡", "卢西娅",
    "原创", "原创1", "原创2", "古薰儿", "古薰儿2", "叶夕水", "叶紫芸", "叶骨衣", "司幼幽", "吟霖",
    "吴懿", "吴茵", "吾妻", "哥伦比娅", "唐月华", "唐舞桐", "四叶真夜", "圣路易斯", "圣采儿2", "圣采儿3",
    "坎特蕾拉", "多角色玉足", "天狐仙子", "天穹长老", "姬凝霜", "姬如雪", "姬青", "娘娘", "宁雨蝶", "守岸人",
    "宋玉", "宋玉1", "宋玉2", "封念云", "封念云2", "小医仙", "小医仙1", "小美人鱼", "小舞", "小舞1",
    "小舞2", "小舞3", "小青", "尤菈", "布洛妮娅", "希诺宁", "建武", "弩S", "徐欣2", "怨仇", "拉克丝",
    "文思月", "新泽西", "方清雪", "易文君", "昔链", "星幻王", "星幻王1", "星见雅", "曹颖", "曹颖1", "曹颖2",
    "有琴玄雅", "朱竹清", "柳七月", "柳玉", "柳玉2", "柳玉3", "柳眉", "桃乐丝", "梅凝", "梦可儿", "梦可儿2",
    "楚萱儿", "楚萱儿2", "橘子", "欧根亲王", "武藏", "汉库克", "江楠楠", "洛璃", "洛璃2", "流萤", "海瑟音",
    "渡边加奈子", "溟莲之主", "溪幼琴", "溪幼琴1", "火允儿", "火允儿1", "火灵儿2", "灵毓秀", "燕如嫣",
    "独孤雁", "玄衣", "玄衣1", "玄衣2", "王琳", "王秋儿", "王秋儿2", "王秋儿3", "玛律恰那", "琳奈",
    "甘璇", "白月蓉", "白雪", "白龙", "碧蓝航线", "神里绫华", "秘书", "穆婉清", "穆碗清", "紫妍", "紫灵",
    "紫灵2", "紫灵3", "紫灵4", "紫萱", "胡妙", "胡滕", "芙宁娜", "芙露德莉斯", "莫斯科", "莫雨", "萧潇",
    "萧潇2", "萧潇3", "蒂法", "蓝梦", "蔷薇", "虞渊初雨", "蚩梦", "调月莉音", "调月莉音2", "貂蝉", "贝拉",
    "赞妮", "远坂凛", "迪盖特鲁因", "邪花侯", "金小钗", "金瓶儿", "银月1", "银狼", "银环", "镜流", "长夜月",
    "长离", "阿格莱雅2", "阿银", "陆嫁嫁", "陆雪琪2", "雅儿贝德", "雉圭", "雉圭2", "雨馨", "雨馨1", "雪帝",
    "雪帝1", "雪帝2", "青仙子", "青仙子2", "青仙子3", "青玉", "马小桃", "齐琪", "龙娇男", "龙娇男2",
    "十三姨", "将臣", "尸魈", "楚宣儿",
}

# 获取所有子文件夹
folders = sorted([f for f in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, f))])

# 分析文件夹名称，提取中文名称
def extract_chinese_name(folder_name):
    """从文件夹名称中提取中文名称（去掉前缀）"""
    # 如果文件夹名称包含下划线，可能有前缀
    if '_' in folder_name:
        parts = folder_name.split('_', 1)
        prefix = parts[0]
        chinese_part = parts[1] if len(parts) > 1 else parts[0]
        # 检查前缀是否只有一个字母
        if len(prefix) == 1 and prefix.isalpha():
            return chinese_part
    return folder_name

# 统计
new_folders = []
existing_folders = []
skipped_folders = []

for folder in folders:
    chinese_name = extract_chinese_name(folder)
    if chinese_name in existing_keys:
        existing_folders.append((folder, chinese_name))
    elif chinese_name.startswith('qvq') or chinese_name.startswith('yande') or chinese_name.startswith('zusy'):
        # 跳过非中文文件夹
        skipped_folders.append((folder, chinese_name))
    else:
        # 生成新的映射
        pinyin_initial = get_pinyin_initial(chinese_name)
        new_folders.append((folder, chinese_name, pinyin_initial, f'"{chinese_name}": "{pinyin_initial}_{chinese_name}"'))

print(f"分析完成！")
print(f"=" * 60)
print(f"总文件夹数: {len(folders)}")
print(f"已存在映射: {len(existing_folders)}")
print(f"新增映射: {len(new_folders)}")
print(f"跳过（非中文）: {len(skipped_folders)}")
print()

if new_folders:
    print("新增映射列表（前20个）：")
    print("-" * 60)
    for item in new_folders[:20]:
        print(f'    {item[3]},')
    if len(new_folders) > 20:
        print(f"    ... 还有 {len(new_folders) - 20} 个")
    print()

# 输出所有新映射供复制
print("=" * 60)
print("所有新增映射（可直接复制到代码中）：")
print("=" * 60)
for item in new_folders:
    print(f'    {item[3]},')
