"""测试文件夹映射逻辑"""
import os
import sys

# 模拟 BatchAutomationPanel 的文件夹映射
folder_mapping = {
    "云望舒": "Y_云望舒",
    "炽阳华明": "C_炽阳华明",
    "燕倾菲": "Y_燕倾菲",
    "云曦": "Y_云曦",
    "云曦1": "Y_云曦",
    "云曦2": "Y_云曦",
    "云曦3": "Y_云曦",
    "云霄": "Y_云霄",
    "云霄2": "Y_云霄",
    "云韵": "Y_云韵",
    "云韵2": "Y_云韵",
    "姜立": "J_姜立",
    "姜力": "J_姜立",  # 注意：这里指向同一个目标
}

def _get_target_folder_new(folder_name):
    """新版本的获取目标文件夹逻辑"""
    # 首先尝试精确匹配
    if folder_name in folder_mapping:
        return os.path.join("E:/output", folder_mapping[folder_name])

    # 然后尝试前缀匹配（处理带编号的文件夹如"云曦1"、"云曦_副本"等）
    for key, value in folder_mapping.items():
        # 检查 folder_name 是否以 key 开头，后面跟随下划线或数字
        if folder_name.startswith(key):
            suffix = folder_name[len(key):]
            # 如果后缀是空的或者是下划线开头的或者是数字开头的，认为是匹配
            if not suffix or suffix.startswith('_') or suffix.isdigit():
                return os.path.join("E:/output", value)

    # 如果没有匹配的映射，返回原文件夹名
    return os.path.join("E:/output", folder_name)


def _get_target_folder_old(folder_name):
    """旧版本的获取目标文件夹逻辑"""
    for key, value in folder_mapping.items():
        if key in folder_name:
            return os.path.join("E:/output", value)
    return os.path.join("E:/output", folder_name)


# 测试用例
test_cases = [
    "云望舒",        # 精确匹配
    "云曦",         # 精确匹配
    "云曦1",        # 前缀匹配（数字后缀）
    "云曦_副本",     # 前缀匹配（下划线后缀）
    "云曦123",      # 前缀匹配（数字后缀）
    "云霄",         # 精确匹配
    "云霄2",        # 前缀匹配（数字后缀）
    "姜立",         # 精确匹配
    "姜力",         # 精确匹配
    "不存在的文件夹", # 无匹配
]

print("=" * 80)
print("测试文件夹映射逻辑")
print("=" * 80)

print("\n新逻辑测试：")
print("-" * 80)
for folder in test_cases:
    result = _get_target_folder_new(folder)
    print(f"文件夹: {folder:15} -> 目标: {result}")

print("\n旧逻辑测试（对比）：")
print("-" * 80)
for folder in test_cases:
    result = _get_target_folder_old(folder)
    print(f"文件夹: {folder:15} -> 目标: {result}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)