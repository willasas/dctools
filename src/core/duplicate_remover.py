"""重复文件删除模块"""
import os
import hashlib
from datetime import datetime
import concurrent.futures
import threading

# 哈希缓存，避免重复计算
hash_cache = {}
# 缓存锁，确保线程安全
hash_cache_lock = threading.Lock()


def get_duplicates_details(folder_path, method="hash", recursive=True, max_workers=8):
    """
    获取重复文件的详细信息
    :param folder_path: 文件夹路径
    :param method: 去重方式（name/size/mtime/hash）
    :param recursive: 是否递归子文件夹
    :param max_workers: 最大线程数，默认8
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
    
    if method == "hash":
        # 使用多线程计算哈希值
        print(f"⚡ 使用多线程计算哈希值，线程数: {max_workers}")
        
        # 存储文件路径和对应的哈希值
        file_hash_map = {}
        
        # 分批处理文件
        batch_size = 100
        total_files = len(files)
        
        for i in range(0, total_files, batch_size):
            batch_files = files[i:i + batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, total_files)
            print(f"\n📦 处理批次 {batch_start}-{batch_end}/{total_files}")
            
            # 使用线程池计算哈希值
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有文件的哈希计算任务
                future_to_file = {executor.submit(get_file_hash, file_path): file_path for file_path in batch_files}
                
                # 处理结果
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        key = future.result()
                        if key:
                            file_hash_map[file_path] = key
                    except Exception as e:
                        print(f"⚠️ 处理文件失败 {file_path}: {str(e)}")
        
        # 构建file_dict
        for file_path, key in file_hash_map.items():
            if key not in file_dict:
                file_dict[key] = []
            file_dict[key].append(file_path)
    else:
        # 其他方法使用单线程处理
        for file_path in files:
            try:
                if method == "name":
                    key = os.path.basename(file_path)
                elif method == "size":
                    key = os.path.getsize(file_path)
                elif method == "mtime":
                    key = os.path.getmtime(file_path)
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


def get_file_hash(file_path, max_file_size=100 * 1024 * 1024):
    """
    计算文件的MD5哈希值
    :param file_path: 文件路径
    :param max_file_size: 最大文件大小（默认100MB），超过此大小的文件将被跳过
    :return: 文件的MD5哈希值
    """
    global hash_cache
    
    # 生成缓存键：文件路径 + 文件修改时间 + 文件大小
    try:
        file_stat = os.stat(file_path)
        cache_key = f"{file_path}_{file_stat.st_mtime}_{file_stat.st_size}"
        
        # 检查缓存
        with hash_cache_lock:
            if cache_key in hash_cache:
                # print(f"📋 从缓存获取哈希值: {file_path}")
                return hash_cache[cache_key]
    except Exception as e:
        print(f"⚠️ 获取文件信息失败 {file_path}: {str(e)}")
        return None
    
    try:
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > max_file_size:
            print(f"⚠️ 跳过大型文件（{file_size/1024/1024:.2f}MB）: {file_path}")
            return None
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):  # 增大缓冲区大小
                hash_md5.update(chunk)
        
        hash_value = hash_md5.hexdigest()
        
        # 存入缓存
        with hash_cache_lock:
            hash_cache[cache_key] = hash_value
        
        return hash_value
    except Exception as e:
        print(f"⚠️ 计算文件哈希失败 {file_path}: {str(e)}")
        return None


def remove_duplicates(folder_path, method="name", dry_run=False, recursive=True, max_workers=8):
    """
    删除重复文件
    :param folder_path: 文件夹路径
    :param method: 去重方式（name/size/mtime/hash）
    :param dry_run: 是否只是预览，不实际删除
    :param recursive: 是否递归子文件夹
    :param max_workers: 最大线程数，默认8
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
    
    if method == "hash":
        # 使用多线程计算哈希值
        print(f"⚡ 使用多线程计算哈希值，线程数: {max_workers}")
        
        # 存储文件路径和对应的哈希值
        file_hash_map = {}
        
        # 分批处理文件
        batch_size = 100
        total_files = len(files)
        
        for i in range(0, total_files, batch_size):
            batch_files = files[i:i + batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, total_files)
            print(f"\n📦 处理批次 {batch_start}-{batch_end}/{total_files}")
            
            # 使用线程池计算哈希值
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有文件的哈希计算任务
                future_to_file = {executor.submit(get_file_hash, file_path): file_path for file_path in batch_files}
                
                # 处理结果
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        key = future.result()
                        if key:
                            file_hash_map[file_path] = key
                    except Exception as e:
                        print(f"⚠️ 处理文件失败 {file_path}: {str(e)}")
        
        # 构建file_dict
        for file_path, key in file_hash_map.items():
            if key not in file_dict:
                file_dict[key] = []
            file_dict[key].append(file_path)
    else:
        # 其他方法使用单线程处理
        for file_path in files:
            try:
                if method == "name":
                    key = os.path.basename(file_path)
                elif method == "size":
                    key = os.path.getsize(file_path)
                elif method == "mtime":
                    key = os.path.getmtime(file_path)
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
    # 批量处理删除操作
    batch_size = 50
    total_duplicates = len(duplicates)
    
    for i in range(0, total_duplicates, batch_size):
        batch_duplicates = duplicates[i:i + batch_size]
        batch_start = i + 1
        batch_end = min(i + batch_size, total_duplicates)
        print(f"\n📦 处理删除批次 {batch_start}-{batch_end}/{total_duplicates}")
        
        for file_path in batch_duplicates:
            try:
                if dry_run:
                    print(f"📋 [预览] 将删除: {file_path}")
                else:
                    os.remove(file_path)
                    print(f"🗑️ 删除: {file_path}")
                removed_count += 1
                # 每10个文件显示一次进度
                if removed_count % 10 == 0:
                    print(f"✅ 已删除 {removed_count}/{total_duplicates} 个文件")
            except Exception as e:
                print(f"❌ 删除失败 {file_path}: {str(e)}")

    print(f"✅ 去重完成！共删除 {removed_count} 个文件")
    return removed_count


def preview_duplicates(folder_path, method="name", recursive=True, max_workers=8):
    """
    预览重复文件
    :param folder_path: 文件夹路径
    :param method: 去重方式
    :param recursive: 是否递归子文件夹
    :param max_workers: 最大线程数，默认8
    :return: 重复文件列表
    """
    return remove_duplicates(folder_path, method, dry_run=True, recursive=recursive, max_workers=max_workers)

