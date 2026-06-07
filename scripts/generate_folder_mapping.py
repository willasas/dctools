"""
生成文件夹名称映射脚本
获取当前文件夹下所有子文件夹名称，并输出格式化的映射数据
"""
import os
import sys

def get_pinyin_initial(text):
    """获取文本的拼音首字母"""
    try:
        from pypinyin import lazy_pinyin
        pinyin_list = lazy_pinyin(text)
        if pinyin_list:
            initial = pinyin_list[0][0].upper()
            return initial
    except ImportError:
        pass
    
    # 如果没有pypinyin库，使用第一个字符
    if text:
        return text[0].upper()
    return 'X'

def generate_folder_mapping(folder_path=None):
    """生成文件夹映射"""
    if folder_path is None:
        folder_path = os.getcwd()
    
    # 获取所有子文件夹
    folders = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            folders.append(item)
    
    if not folders:
        print("当前文件夹下没有子文件夹")
        return
    
    # 排序
    folders.sort()
    
    # 生成映射
    print('folder_mapping = {')
    for folder in folders:
        initial = get_pinyin_initial(folder)
        print(f'    "{folder}": "{initial}_{folder}",')
    print('}')

if __name__ == '__main__':
    # 如果提供了参数，使用参数作为路径
    if len(sys.argv) > 1:
        target_path = sys.argv[1]
    else:
        target_path = None
    
    print(f"// 文件夹路径: {target_path if target_path else os.getcwd()}")
    print()
    generate_folder_mapping(target_path)