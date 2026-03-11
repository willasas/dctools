"""文件重命名模块"""
import os
import re
import shutil
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


def add_prefix_suffix(file_name, prefix="", suffix="", position="end"):
    """
    添加前缀和后缀
    :param file_name: 文件名
    :param prefix: 前缀
    :param suffix: 后缀
    :param position: 后缀位置 (end: 末尾, before_ext: 扩展名前)
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    if position == "before_ext":
        return f"{prefix}{name_part}{suffix}{ext}"
    else:  # end
        return f"{prefix}{name_part}{ext}{suffix}"


def replace_text(file_name, find_text, replace_text, case_sensitive=True):
    """
    替换文本
    :param file_name: 文件名
    :param find_text: 要查找的文本
    :param replace_text: 要替换的文本
    :param case_sensitive: 是否区分大小写
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    if case_sensitive:
        new_name_part = name_part.replace(find_text, replace_text)
    else:
        import re
        new_name_part = re.sub(re.escape(find_text), replace_text, name_part, flags=re.IGNORECASE)

    return f"{new_name_part}{ext}"


def replace_regex(file_name, pattern, replacement, flags=0):
    """
    使用正则表达式替换文本
    :param file_name: 文件名
    :param pattern: 正则表达式模式
    :param replacement: 替换文本
    :param flags: 正则表达式标志
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    new_name_part = re.sub(pattern, replacement, name_part, flags=flags)

    return f"{new_name_part}{ext}"


def change_case(file_name, case_type="title"):
    """
    更改大小写
    :param file_name: 文件名
    :param case_type: 大小写类型 (lower: 小写, upper: 大写, title: 标题, sentence: 句子)
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    if case_type == "lower":
        new_name_part = name_part.lower()
    elif case_type == "upper":
        new_name_part = name_part.upper()
    elif case_type == "title":
        new_name_part = name_part.title()
    elif case_type == "sentence":
        new_name_part = name_part.capitalize()
    else:
        new_name_part = name_part

    return f"{new_name_part}{ext}"


def remove_brackets_content(file_name, brackets_types=["()", "[]", "{}"]):
    """
    删除括号内容
    :param file_name: 文件名
    :param brackets_types: 括号类型列表
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    for brackets in brackets_types:
        if len(brackets) == 2:
            open_bracket, close_bracket = brackets[0], brackets[1]
            # 使用正则表达式删除括号及其内容
            pattern = f"\\{open_bracket}[^\\{open_bracket}\\{close_bracket}]*\\{close_bracket}"
            name_part = re.sub(pattern, "", name_part)

    # 去除多余的空格
    name_part = re.sub(r"\s+", " ", name_part).strip()

    return f"{name_part}{ext}"


def change_extension(file_name, new_extension):
    """
    更改文件扩展名
    :param file_name: 文件名
    :param new_extension: 新扩展名（不含点）
    :return: 新文件名
    """
    name_part, _ = os.path.splitext(file_name)

    if new_extension:
        if not new_extension.startswith("."):
            new_extension = f".{new_extension}"
    else:
        new_extension = ""

    return f"{name_part}{new_extension}"


def remove_spaces(file_name, replace_with="_"):
    """
    移除空格
    :param file_name: 文件名
    :param replace_with: 替换空格的字符，默认为下划线
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    new_name_part = name_part.replace(" ", replace_with)

    return f"{new_name_part}{ext}"


def add_datetime(file_name, format="%Y%m%d", position="before_ext"):
    """
    添加日期时间
    :param file_name: 文件名
    :param format: 日期时间格式，默认为%Y%m%d（年-月-日）
    :param position: 添加位置 (before_ext: 扩展名前, start: 开头, end: 末尾)
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    datetime_str = datetime.now().strftime(format)

    if position == "before_ext":
        return f"{name_part}_{datetime_str}{ext}"
    elif position == "start":
        return f"{datetime_str}_{name_part}{ext}"
    else:  # end
        return f"{name_part}{ext}_{datetime_str}"


def add_random_string(file_name, length=6, position="before_ext"):
    """
    添加随机字符串
    :param file_name: 文件名
    :param length: 随机字符串长度，默认为6
    :param position: 添加位置 (before_ext: 扩展名前, start: 开头, end: 末尾)
    :return: 新文件名
    """
    import random
    import string

    name_part, ext = os.path.splitext(file_name)

    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    if position == "before_ext":
        return f"{name_part}_{random_str}{ext}"
    elif position == "start":
        return f"{random_str}_{name_part}{ext}"
    else:  # end
        return f"{name_part}{ext}_{random_str}"


def add_smart_numbering(file_name, index, digits=3, start_value=1, increment=1):
    """
    添加智能序号
    :param file_name: 文件名
    :param index: 当前序号
    :param digits: 序号位数，默认为3
    :param start_value: 起始值，默认为1
    :param increment: 增量，默认为1
    :return: 新文件名
    """
    name_part, ext = os.path.splitext(file_name)

    # 计算实际序号
    actual_number = start_value + (index - 1) * increment
    formatted_number = format_number_with_digits(actual_number, digits)

    return f"{name_part}_{formatted_number}{ext}"


def apply_rename_rules(file_name, rules):
    """
    应用多个重命名规则
    :param file_name: 原文件名
    :param rules: 规则列表，每个规则是一个字典，包含规则类型和参数
    :return: 新文件名
    """
    new_name = file_name

    for rule in rules:
        rule_type = rule.get("type")

        if rule_type == "prefix_suffix":
            new_name = add_prefix_suffix(
                new_name,
                prefix=rule.get("prefix", ""),
                suffix=rule.get("suffix", ""),
                position=rule.get("position", "end")
            )
        elif rule_type == "replace":
            new_name = replace_text(
                new_name,
                find_text=rule.get("find", ""),
                replace_text=rule.get("replace", ""),
                case_sensitive=rule.get("case_sensitive", True)
            )
        elif rule_type == "regex":
            new_name = replace_regex(
                new_name,
                pattern=rule.get("pattern", ""),
                replacement=rule.get("replacement", ""),
                flags=rule.get("flags", 0)
            )
        elif rule_type == "case":
            new_name = change_case(
                new_name,
                case_type=rule.get("case_type", "title")
            )
        elif rule_type == "remove_brackets":
            new_name = remove_brackets_content(
                new_name,
                brackets_types=rule.get("brackets_types", ["()", "[]", "{}"])
            )
        elif rule_type == "extension":
            new_name = change_extension(
                new_name,
                new_extension=rule.get("new_extension", "")
            )
        elif rule_type == "remove_spaces":
            new_name = remove_spaces(
                new_name,
                replace_with=rule.get("replace_with", "_")
            )
        elif rule_type == "add_datetime":
            new_name = add_datetime(
                new_name,
                format=rule.get("format", "%Y%m%d"),
                position=rule.get("position", "before_ext")
            )
        elif rule_type == "add_random_string":
            new_name = add_random_string(
                new_name,
                length=rule.get("length", 6),
                position=rule.get("position", "before_ext")
            )

    return new_name


def batch_rename_with_rules(folder_path, rules, include_hidden=False, recursive=False):
    """
    使用规则批量重命名文件
    :param folder_path: 文件夹路径
    :param rules: 重命名规则列表
    :param include_hidden: 是否包含隐藏文件
    :param recursive: 是否递归子文件夹
    :return: 重命名结果字典
    """
    try:
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"文件夹不存在: {folder_path}")

        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"路径不是文件夹: {folder_path}")

        if not os.access(folder_path, os.W_OK):
            raise PermissionError(f"没有写入权限: {folder_path}")

        if not rules:
            raise ValueError("重命名规则不能为空")

        print(f"\n🔄 开始批量重命名...")
        print(f"   文件夹: {folder_path}")
        print(f"   递归: {'是' if recursive else '否'}")
        print(f"   包含隐藏文件: {'是' if include_hidden else '否'}")
        print(f"   应用规则数: {len(rules)}")

        # 获取所有文件
        files = []
        try:
            if recursive:
                for root, _, filenames in os.walk(folder_path):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if include_hidden or not filename.startswith('.'):
                            files.append((root, filename))
            else:
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        if include_hidden or not filename.startswith('.'):
                            files.append((folder_path, filename))
        except Exception as e:
            print(f"❌ 获取文件列表失败: {str(e)}")
            return {"renamed": [], "failed": [], "error": str(e)}

        print(f"\n📊 找到 {len(files)} 个文件")

        # 重命名文件
        renamed_files = []
        failed_files = []

        for root, old_name in files:
            try:
                old_path = os.path.join(root, old_name)

                # 检查文件是否存在且可访问
                if not os.path.exists(old_path):
                    print(f"⚠️ 文件不存在: {old_name}")
                    failed_files.append(old_name)
                    continue

                if not os.access(old_path, os.W_OK):
                    print(f"⚠️ 没有文件写入权限: {old_name}")
                    failed_files.append(old_name)
                    continue

                # 应用重命名规则
                try:
                    new_name = apply_rename_rules(old_name, rules)
                except Exception as e:
                    print(f"❌ 应用规则失败: {old_name} - {str(e)}")
                    failed_files.append(old_name)
                    continue

                # 检查新文件名是否与原文件名相同
                if new_name == old_name:
                    print(f"⚠️ 文件名未更改: {old_name}")
                    continue

                # 检查新文件名是否有效
                if not new_name:
                    print(f"⚠️ 生成的文件名为空: {old_name}")
                    failed_files.append(old_name)
                    continue

                # 检查新文件名是否包含无效字符
                invalid_chars = '<>"|?*'
                if any(char in new_name for char in invalid_chars):
                    print(f"⚠️ 文件名包含无效字符: {new_name}")
                    failed_files.append(old_name)
                    continue

                new_path = os.path.join(root, new_name)

                # 检查新文件名是否已存在
                if os.path.exists(new_path):
                    print(f"⚠️ 文件已存在，跳过: {new_name}")
                    failed_files.append(old_name)
                    continue

                # 检查新文件路径是否可写
                if not os.access(root, os.W_OK):
                    print(f"⚠️ 没有目录写入权限: {root}")
                    failed_files.append(old_name)
                    continue

                # 重命名文件
                try:
                    os.rename(old_path, new_path)
                    renamed_files.append((old_name, new_name))
                    print(f"✅ 重命名成功: {old_name} -> {new_name}")
                except Exception as e:
                    print(f"❌ 重命名失败: {old_name} - {str(e)}")
                    failed_files.append(old_name)
                    continue
            except Exception as e:
                print(f"❌ 处理文件失败: {old_name} - {str(e)}")
                failed_files.append(old_name)
                continue

    except Exception as e:
        print(f"❌ 批量重命名失败: {str(e)}")
        return {"renamed": [], "failed": [], "error": str(e)}

    print(f"\n✅ 批量重命名完成！")
    print(f"   成功: {len(renamed_files)} 个文件")
    print(f"   失败: {len(failed_files)} 个文件")

    return {
        "renamed": renamed_files,
        "failed": failed_files
    }

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


def preview_rename_with_rules(folder_path, rules, include_hidden=False, recursive=False):
    """
    使用规则预览重命名结果
    :param folder_path: 文件夹路径
    :param rules: 重命名规则列表
    :param include_hidden: 是否包含隐藏文件
    :param recursive: 是否递归子文件夹
    :return: 预览结果列表
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    print(f"\n🔍 重命名规则预览:")
    print(f"   文件夹: {folder_path}")
    print(f"   递归: {'是' if recursive else '否'}")
    print(f"   包含隐藏文件: {'是' if include_hidden else '否'}")
    print(f"   应用规则数: {len(rules)}")

    # 获取所有文件
    files = []
    if recursive:
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if include_hidden or not filename.startswith('.'):
                    files.append((root, filename))
    else:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                if include_hidden or not filename.startswith('.'):
                    files.append((folder_path, filename))

    # 按文件名排序
    files.sort(key=lambda x: x[1])

    print(f"\n📊 找到 {len(files)} 个文件")

    # 生成预览
    preview_list = []
    for root, old_name in files:
        try:
            # 应用重命名规则
            new_name = apply_rename_rules(old_name, rules)

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


def batch_move_files(file_paths, target_folder, overwrite=False, batch_size=50):
    """
    批量移动文件到指定文件夹
    :param file_paths: 文件路径列表
    :param target_folder: 目标文件夹路径
    :param overwrite: 是否覆盖已存在的文件
    :param batch_size: 批处理大小，默认50个文件一批
    :return: 移动结果字典
    """
    try:
        if not file_paths:
            raise ValueError("文件路径列表为空")

        if not target_folder:
            raise ValueError("目标文件夹路径为空")

        # 确保目标文件夹存在
        os.makedirs(target_folder, exist_ok=True)

        print(f"\n🔄 开始批量移动文件...")
        print(f"   目标文件夹: {target_folder}")
        print(f"   文件数量: {len(file_paths)}")
        print(f"   覆盖模式: {'是' if overwrite else '否'}")
        print(f"   批处理大小: {batch_size}")

        # 移动文件
        moved_files = []
        failed_files = []
        total_files = len(file_paths)

        # 批量处理文件
        for i in range(0, total_files, batch_size):
            batch_files = file_paths[i:i + batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, total_files)
            print(f"\n📦 处理批次 {batch_start}-{batch_end}/{total_files}")

            for file_path in batch_files:
                try:
                    # 检查文件是否存在
                    if not os.path.exists(file_path):
                        print(f"⚠️ 文件不存在: {file_path}")
                        failed_files.append(file_path)
                        continue

                    # 检查文件是否可访问
                    if not os.access(file_path, os.R_OK):
                        print(f"⚠️ 没有文件读取权限: {file_path}")
                        failed_files.append(file_path)
                        continue

                    # 获取文件名
                    file_name = os.path.basename(file_path)
                    target_path = os.path.join(target_folder, file_name)

                    # 检查目标文件是否已存在
                    if os.path.exists(target_path):
                        if overwrite:
                            print(f"⚠️ 文件已存在，将覆盖: {file_name}")
                            os.remove(target_path)
                        else:
                            print(f"⚠️ 文件已存在，跳过: {file_name}")
                            failed_files.append(file_path)
                            continue

                    # 检查目标文件夹是否可写
                    if not os.access(target_folder, os.W_OK):
                        print(f"⚠️ 没有目标文件夹写入权限: {target_folder}")
                        failed_files.append(file_path)
                        continue

                    # 移动文件
                    try:
                        shutil.move(file_path, target_path)
                        moved_files.append((file_path, target_path))
                        # 每10个文件显示一次进度
                        if len(moved_files) % 10 == 0:
                            print(f"✅ 已移动 {len(moved_files)}/{total_files} 个文件")
                    except Exception as e:
                        print(f"❌ 移动失败: {file_name} - {str(e)}")
                        failed_files.append(file_path)
                        continue

                except Exception as e:
                    print(f"❌ 处理文件失败: {file_path} - {str(e)}")
                    failed_files.append(file_path)
                    continue

        print(f"\n✅ 批量移动完成！")
        print(f"   成功: {len(moved_files)} 个文件")
        print(f"   失败: {len(failed_files)} 个文件")

        return {
            "moved": moved_files,
            "failed": failed_files
        }

    except Exception as e:
        print(f"❌ 批量移动失败: {str(e)}")
        return {"moved": [], "failed": [], "error": str(e)}


def preview_move(file_paths, target_folder):
    """
    预览移动结果
    :param file_paths: 文件路径列表
    :param target_folder: 目标文件夹路径
    :return: 预览结果列表
    """
    if not file_paths:
        raise ValueError("文件路径列表为空")

    if not target_folder:
        raise ValueError("目标文件夹路径为空")

    print(f"\n🔍 移动预览:")
    print(f"   目标文件夹: {target_folder}")
    print(f"   文件数量: {len(file_paths)}")

    # 生成预览
    preview_list = []
    for file_path in file_paths:
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"⚠️ 文件不存在: {file_path}")
                continue

            # 获取文件名
            file_name = os.path.basename(file_path)
            target_path = os.path.join(target_folder, file_name)

            # 检查目标文件是否已存在
            if os.path.exists(target_path):
                print(f"⚠️ 目标文件已存在: {file_name}")
            else:
                print(f"   {file_name} -> {target_folder}")

            preview_list.append((file_path, target_path))

        except Exception as e:
            print(f"❌ 预览失败: {file_path} - {str(e)}")

    return preview_list
