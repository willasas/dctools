"""文件夹创建模块"""
import os
from pypinyin import pinyin, Style

def get_chinese_initial(chinese_name):
    """获取中文名称的首字母大写"""
    if not chinese_name or not isinstance(chinese_name, str):
        return ""
    
    first_char = chinese_name[0]
    pinyin_result = pinyin(first_char, style=Style.FIRST_LETTER)
    if pinyin_result and pinyin_result[0]:
        return pinyin_result[0][0].upper()
    
    return ""

def create_single_folder(chinese_name, parent_path=".", use_initial_naming=True):
    """
    创建单个文件夹（使用首字母命名规则）
    :param chinese_name: 中文名称
    :param parent_path: 父路径
    :param use_initial_naming: 是否使用首字母命名规则
    :return: 文件夹路径
    """
    try:
        # 强制使用首字母命名规则
        initial = get_chinese_initial(chinese_name)
        folder_name = f"{initial}_{chinese_name}" if initial else chinese_name
        
        folder_path = os.path.join(parent_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ 创建文件夹: {folder_path}")
        return folder_path
    except Exception as e:
        print(f"❌ 创建文件夹失败: {str(e)}")
        return None

def batch_create_folders(folder_list, use_initial_naming=True):
    """
    批量创建文件夹
    :param folder_list: 文件夹信息列表
    :param use_initial_naming: 是否使用首字母命名规则
    :return: 创建成功的文件夹路径列表
    """
    created_folders = []
    for folder_info in folder_list:
        name = folder_info.get("name", "")
        path = folder_info.get("path", ".")
        if name:
            folder_path = create_single_folder(name, path, use_initial_naming)
            if folder_path:
                created_folders.append(folder_path)
    return created_folders
