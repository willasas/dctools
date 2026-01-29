"""文件夹信息模块"""
import os
import json
from datetime import datetime


def get_folder_info(folder_path, recursive=True):
    """
    获取文件夹详细信息
    :param folder_path: 文件夹路径
    :param recursive: 是否递归子文件夹
    :return: 文件夹信息字典
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    if not os.path.isdir(folder_path):
        raise ValueError(f"路径不是文件夹: {folder_path}")

    print(f"\n📁 开始分析文件夹: {folder_path}")

    info = {
        "folder_path": folder_path,
        "folder_name": os.path.basename(folder_path),
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": 0,
        "total_folders": 0,
        "total_size": 0,
        "file_types": {},
        "subfolders": []
    }

    # 分析文件夹
    _analyze_folder(folder_path, info, recursive)

    # 格式化大小
    info["total_size_formatted"] = _format_size(info["total_size"])

    print(f"✅ 文件夹分析完成!")
    print(f"   文件数量: {info['total_files']}")
    print(f"   文件夹数量: {info['total_folders']}")
    print(f"   总大小: {info['total_size_formatted']}")
    print(f"   文件类型: {list(info['file_types'].keys())}")

    return info


def _analyze_folder(folder_path, info, recursive):
    """
    递归分析文件夹
    :param folder_path: 文件夹路径
    :param info: 信息字典
    :param recursive: 是否递归
    """
    info["total_folders"] += 1

    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            if os.path.isfile(item_path):
                # 分析文件
                info["total_files"] += 1

                # 计算大小
                size = os.path.getsize(item_path)
                info["total_size"] += size

                # 分析文件类型
                ext = os.path.splitext(item)[1].lower()
                if ext not in info["file_types"]:
                    info["file_types"][ext] = {
                        "count": 0,
                        "total_size": 0
                    }
                info["file_types"][ext]["count"] += 1
                info["file_types"][ext]["total_size"] += size
                info["file_types"][ext]["total_size_formatted"] = _format_size(info["file_types"][ext]["total_size"])

            elif os.path.isdir(item_path) and recursive:
                # 递归分析子文件夹
                subfolder_info = {
                    "name": item,
                    "path": item_path,
                    "files": 0,
                    "folders": 0,
                    "size": 0
                }

                # 递归分析
                _analyze_subfolder(item_path, subfolder_info)

                # 格式化大小
                subfolder_info["size_formatted"] = _format_size(subfolder_info["size"])

                info["subfolders"].append(subfolder_info)

    except Exception as e:
        print(f"⚠️ 分析文件夹失败 {folder_path}: {str(e)}")


def _analyze_subfolder(folder_path, info):
    """
    分析子文件夹
    :param folder_path: 文件夹路径
    :param info: 信息字典
    """
    info["folders"] += 1

    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            if os.path.isfile(item_path):
                info["files"] += 1
                info["size"] += os.path.getsize(item_path)
            elif os.path.isdir(item_path):
                _analyze_subfolder(item_path, info)

    except Exception as e:
        print(f"⚠️ 分析子文件夹失败 {folder_path}: {str(e)}")


def analyze_folder_structure(folder_path, output_format="json"):
    """
    分析文件夹结构并输出
    :param folder_path: 文件夹路径
    :param output_format: 输出格式 (json/text)
    :return: 分析结果
    """
    info = get_folder_info(folder_path)

    if output_format == "json":
        result = json.dumps(info, ensure_ascii=False, indent=2)
        print("\n📋 文件夹分析结果 (JSON):")
        print(result)
        return result
    else:
        # 文本格式输出
        result = []
        result.append(f"文件夹分析报告")
        result.append(f"=" * 50)
        result.append(f"分析时间: {info['analysis_time']}")
        result.append(f"文件夹路径: {info['folder_path']}")
        result.append(f"文件夹名称: {info['folder_name']}")
        result.append(f"总文件数: {info['total_files']}")
        result.append(f"总文件夹数: {info['total_folders']}")
        result.append(f"总大小: {info['total_size_formatted']}")
        result.append(f"")
        result.append(f"文件类型分布:")
        result.append(f"-" * 30)

        for ext, type_info in info['file_types'].items():
            result.append(f"{ext}: {type_info['count']}个文件, {type_info['total_size_formatted']}")

        if info['subfolders']:
            result.append(f"")
            result.append(f"子文件夹信息:")
            result.append(f"-" * 30)
            for subfolder in info['subfolders']:
                result.append(f"{subfolder['name']}: {subfolder['files']}个文件, {subfolder['folders']}个文件夹, {subfolder['size_formatted']}")

        result_text = "\n".join(result)
        print("\n📋 文件夹分析结果 (文本):")
        print(result_text)
        return result_text


def _format_size(size_bytes):
    """
    格式化文件大小
    :param size_bytes: 字节大小
    :return: 格式化后的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
