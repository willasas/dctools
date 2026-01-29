"""重复文件删除模块"""
import os
import hashlib
from datetime import datetime


def get_duplicates_details(folder_path, method="hash", recursive=True):
    """
    获取重复文件的详细信息
    :param folder_path: 文件夹路径
    :param method: 去重方式（name/size/mtime/hash）
    :param recursive: 是否递归子文件夹
    :return: 重复文件分组列表
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    print(f"\n🔍 开始扫描重复文件: {folder_path}")
    print(f"   方式: {method}")
    print(f"   递归: {'是' if recursive else '否'}")

    # 获取所有文件
    files = []
    if recursive:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    files.append(file_path)
    else:
        # 只扫描当前文件夹
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                files.append(file_path)

    if len(files) < 2:
        print("⚠️ 文件数量不足，无需去重")
        return []

    print(f"📊 找到 {len(files)} 个文件")

    # 根据方法获取文件标识
    file_dict = {}
    for file_path in files:
        try:
            if method == "name":
                key = os.path.basename(file_path)
            elif method == "size":
                key = os.path.getsize(file_path)
            elif method == "mtime":
                key = os.path.getmtime(file_path)
            elif method == "hash":
                key = get_file_hash(file_path)
            else:
                raise ValueError(f"未知的去重方式: {method}")

            if key not in file_dict:
                file_dict[key] = []
            file_dict[key].append(file_path)
        except Exception as e:
            print(f"⚠️ 处理文件失败 {file_path}: {str(e)}")

    # 返回有重复的文件组
    duplicates_groups = []
    for key, file_list in file_dict.items():
        if len(file_list) > 1:
            duplicates_groups.append({
                'key': key,
                'files': file_list
            })

    print(f"🔍 发现 {len(duplicates_groups)} 组重复文件")
    return duplicates_groups


def get_file_hash(file_path):
    """计算文件的MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def remove_duplicates(folder_path, method="name", dry_run=False, recursive=True):
    """
    删除重复文件
    :param folder_path: 文件夹路径
    :param method: 去重方式（name/size/mtime/hash）
    :param dry_run: 是否只是预览，不实际删除
    :param recursive: 是否递归子文件夹
    :return: 删除的文件数量
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    print(f"\n🔍 开始去重: {folder_path}")
    print(f"   方式: {method}")
    print(f"   模式: {'预览' if dry_run else '执行'}")
    print(f"   递归: {'是' if recursive else '否'}")

    # 获取所有文件
    files = []
    if recursive:
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    files.append(file_path)
    else:
        # 只扫描当前文件夹
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                files.append(file_path)

    if len(files) < 2:
        print("⚠️ 文件数量不足，无需去重")
        return 0

    print(f"📊 找到 {len(files)} 个文件")

    # 根据方法获取文件标识
    file_dict = {}
    for file_path in files:
        try:
            if method == "name":
                key = os.path.basename(file_path)
            elif method == "size":
                key = os.path.getsize(file_path)
            elif method == "mtime":
                key = os.path.getmtime(file_path)
            elif method == "hash":
                key = get_file_hash(file_path)
            else:
                raise ValueError(f"未知的去重方式: {method}")

            if key not in file_dict:
                file_dict[key] = []
            file_dict[key].append(file_path)
        except Exception as e:
            print(f"⚠️ 处理文件失败 {file_path}: {str(e)}")

    # 找出重复文件
    duplicates = []
    for key, file_list in file_dict.items():
        if len(file_list) > 1:
            # 保留第一个，其余的标记为重复
            duplicates.extend(file_list[1:])

    print(f"🔍 发现 {len(duplicates)} 个重复文件")

    # 删除或预览
    removed_count = 0
    for file_path in duplicates:
        try:
            if dry_run:
                print(f"📋 [预览] 将删除: {file_path}")
            else:
                os.remove(file_path)
                print(f"🗑️ 删除: {file_path}")
            removed_count += 1
        except Exception as e:
            print(f"❌ 删除失败 {file_path}: {str(e)}")

    print(f"✅ 去重完成！共删除 {removed_count} 个文件")
    return removed_count


def preview_duplicates(folder_path, method="name", recursive=True):
    """
    预览重复文件
    :param folder_path: 文件夹路径
    :param method: 去重方式
    :param recursive: 是否递归子文件夹
    :return: 重复文件列表
    """
    return remove_duplicates(folder_path, method, dry_run=True, recursive=recursive)

