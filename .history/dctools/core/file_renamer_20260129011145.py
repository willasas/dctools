"""文件重命名模块"""
import os
import re
from datetime import datetime
from pypinyin import pinyin, Style

def get_file_type(file_path):
    """获取文件类型"""
    ext = os.path.splitext(file_path)[1].lower()
    type_mapping = {
        '.jpg': 'picture', '.jpeg': 'picture', '.png': 'picture', '.gif': 'picture', '.bmp': 'picture', '.webp': 'picture',
        '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.mkv': 'video', '.flv': 'video', '.wmv': 'video',
        '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio', '.aac': 'audio',
        '.pdf': 'document', '.doc': 'document', '.docx': 'document', '.txt': 'document', '.xls': 'document', '.xlsx': 'document', '.ppt': 'document', '.pptx': 'document'
    }
    return type_mapping.get(ext, 'file')

def get_pinyin_name(chinese_name, with_underscore=True):
    """获取中文名称的拼音"""
    if not chinese_name:
        return ""
    pinyin_result = pinyin(chinese_name, style=Style.NORMAL)
    if with_underscore:
        return '_'.join([item[0] for item in pinyin_result])
    else:
        return ''.join([item[0] for item in pinyin_result])

def format_number_with_digits(number, digits):
    """将数字格式化为指定位数，不足补0"""
    return str(number).zfill(digits)

def generate_new_name(file_path, chinese_name, naming_rule, index, timestamp,
                     pinyin_name, file_type, start_value=0, digits=1, increment=1):
    """
    生成新的文件名
    :param file_path: 原文件路径
    :param chinese_name: 中文名称
    :param naming_rule: 命名规则
    :param index: 当前序号（从1开始）
    :param timestamp: 时间戳
    :param pinyin_name: 拼音名称
    :param file_type: 文件类型
    :param start_value: 初始值
    :param digits: 位数
    :param increment: 增量
    :return: 新文件名
    """
    ext = os.path.splitext(file_path)[1]

    # 计算实际序号：初始值 + (当前序号-1) * 增量
    actual_number = start_value + (index - 1) * increment

    # 格式化序号为指定位数
    formatted_number = format_number_with_digits(actual_number, digits)

    # 替换命名规则中的变量
    new_name = naming_rule.format(
        pinyin_name=pinyin_name,
        index=formatted_number,
        timestamp=timestamp,
        type=file_type,
        chinese_name=chinese_name
    )

    return f"{new_name}{ext}"

def get_default_naming_rule(use_chinese=False):
    """获取默认命名规则"""
    if use_chinese:
        return "{type}_{pinyin_name}({chinese_name})_{timestamp}_{index}"
    else:
        return "{type}_{pinyin_name}_{timestamp}_{index}"


def get_default_timestamp():
    """获取默认时间戳格式"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_simple_timestamp():
    """获取简单时间戳格式（不带下划线）"""
    return datetime.now().strftime("%Y%m%d%H%M%S")

def preview_rename(folder_path, chinese_name, start_value=0, digits=1, increment=1):
    """
    预览重命名结果
    :param folder_path: 文件夹路径
    :param chinese_name: 中文名称
    :param start_value: 初始值
    :param digits: 位数
    :param increment: 增量
    :return: 预览结果列表
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    print("\n🔍 重命名预览:")
    print(f"   文件夹: {folder_path}")
    print(f"   中文名称: {chinese_name}")
    print(f"   初始值: {start_value}")
    print(f"   位数: {digits}")
    print(f"   增量: {increment}")

    # 获取所有文件
    files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and not file.startswith('.'):
            files.append(file)

    # 按文件名排序
    files.sort()

    print(f"\n📊 找到 {len(files)} 个文件")

    # 生成时间戳
    timestamp = get_default_timestamp()

    # 获取拼音名称
    pinyin_name = get_pinyin_name(chinese_name, with_underscore=True)

    # 生成预览
    preview_list = []
    for index, old_name in enumerate(files, start=1):
        try:
            old_path = os.path.join(folder_path, old_name)
            file_type = get_file_type(old_path)

            # 生成新文件名（使用默认规则）
            naming_rule = get_default_naming_rule()
            new_name = generate_new_name(
                old_path, chinese_name, naming_rule, index,
                timestamp, pinyin_name, file_type,
                start_value, digits, increment
            )

            preview_list.append((old_name, new_name))
            print(f"   {old_name} -> {new_name}")

        except Exception as e:
            print(f"❌ 预览失败: {old_name} - {str(e)}")

    return preview_list

def batch_rename_files(folder_path, chinese_name, naming_rule=None,
                      start_value=0, digits=1, increment=1, include_hidden=False,
                      with_underscore=True, include_chinese=False):
    """
    批量重命名文件夹中的文件
    :param folder_path: 文件夹路径
    :param chinese_name: 中文名称
    :param naming_rule: 命名规则（支持变量：{pinyin_name}, {index}, {timestamp}, {type}, {chinese_name}）
    :param start_value: 初始值（默认0）
    :param digits: 位数（默认1）
    :param increment: 增量（默认1）
    :param include_hidden: 是否包含隐藏文件
    :param with_underscore: 拼音是否使用下划线连接
    :param include_chinese: 是否在文件名中包含中文
    :return: 重命名成功的文件列表
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    print("\n🔄 开始批量重命名...")
    print(f"   文件夹: {folder_path}")
    print(f"   中文名称: {chinese_name}")
    print(f"   初始值: {start_value}")
    print(f"   位数: {digits}")
    print(f"   增量: {increment}")
    print(f"   包含隐藏文件: {'是' if include_hidden else '否'}")
    print(f"   拼音下划线: {'是' if with_underscore else '否'}")
    print(f"   包含中文: {'是' if include_chinese else '否'}")

    # 获取所有文件
    files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            if include_hidden or not file.startswith('.'):
                files.append(file)

    # 按文件名排序
    files.sort()

    print(f"\n📊 找到 {len(files)} 个文件")

    # 生成时间戳
    timestamp = get_simple_timestamp()  # 使用不带下划线的时间戳

    # 获取拼音名称
    pinyin_name = get_pinyin_name(chinese_name, with_underscore=with_underscore)

    # 使用默认命名规则
    if not naming_rule:
        naming_rule = get_default_naming_rule(use_chinese=include_chinese)

    print(f"\n📋 使用命名规则: {naming_rule}")

    # 重命名文件
    renamed_files = []
    failed_files = []

    for index, old_name in enumerate(files, start=1):
        try:
            old_path = os.path.join(folder_path, old_name)
            file_type = get_file_type(old_path)

            # 生成新文件名
            new_name = generate_new_name(
                old_path, chinese_name, naming_rule, index,
                timestamp, pinyin_name, file_type,
                start_value, digits, increment
            )

            new_path = os.path.join(folder_path, new_name)

            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                print(f"⚠️ 文件已存在，跳过: {new_name}")
                failed_files.append(old_name)
                continue

            # 重命名文件
            os.rename(old_path, new_path)
            renamed_files.append(new_path)
            print(f"✅ 重命名成功: {old_name} -> {new_name}")

            # 显示进度
            if index % 10 == 0 or index == len(files):
                print(f"   进度: {index}/{len(files)}")

        except Exception as e:
            print(f"❌ 重命名失败: {old_name} - {str(e)}")
            failed_files.append(old_name)

    print(f"\n✅ 批量重命名完成！")
    print(f"   成功: {len(renamed_files)} 个文件")
    print(f"   失败: {len(failed_files)} 个文件")

    return renamed_files
