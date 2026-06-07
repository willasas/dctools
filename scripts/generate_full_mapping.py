# 生成完整的folder_mapping.json
import os
import json
from pypinyin import pinyin, Style

def get_pinyin_initial(name):
    """获取第一个汉字的拼音首字母"""
    try:
        for item in pinyin(name, style=Style.NORMAL):
            if item and len(item) > 0 and item[0]:
                return item[0][0]
    except:
        pass
    return 'Z'

# 目标文件夹
target_dir = r'E:\AI玲珑\壁纸'

# 读取所有子文件夹
folders = []
for item in sorted(os.listdir(target_dir)):
    item_path = os.path.join(target_dir, item)
    if os.path.isdir(item_path):
        folders.append(item)

print(f"找到 {len(folders)} 个子文件夹")

# 构建映射表
mapping = {}

for folder in folders:
    # 提取中文名称（去除前缀如 Y_）
    chinese_name = folder
    if '_' in folder:
        parts = folder.split('_', 1)
        if len(parts[0]) == 1 and parts[0].isalpha():
            chinese_name = parts[1]
    
    # 跳过不需要添加的
    if not chinese_name or not any('\u4e00' <= c <= '\u9fff' for c in chinese_name):
        continue
    
    # 生成映射
    initial = get_pinyin_initial(chinese_name).upper()
    mapping[chinese_name] = f"{initial}_{chinese_name}"

print(f"生成 {len(mapping)} 个映射")

# 保存到文件
output_file = r'd:\VDhub\dctools\src\config\folder_mapping.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

print(f"映射表已保存到: {output_file}")

# 验证
print("\n验证部分映射:")
for i, (name, value) in enumerate(list(mapping.items())[:20]):
    print(f"  {name}: {value}")
print(f"  ... 还有 {len(mapping)-20} 个")
