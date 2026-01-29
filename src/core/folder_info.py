"""文件夹信息模块"""
import os
import json
import csv
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
    
    _analyze_folder(folder_path, info, recursive)
    
    info["total_size_formatted"] = _format_size(info["total_size"])
    
    print(f"✅ 文件夹分析完成!")
    print(f"   文件数量: {info['total_files']}")
    print(f"   文件夹数量: {info['total_folders']}")
    print(f"   总大小: {info['total_size_formatted']}")
    print(f"   文件类型: {list(info['file_types'].keys())}")
    
    return info


def _analyze_folder(folder_path, info, recursive):
    """递归分析文件夹"""
    info["total_folders"] += 1
    
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            if os.path.isfile(item_path):
                info["total_files"] += 1
                size = os.path.getsize(item_path)
                info["total_size"] += size
                
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
                subfolder_info = {
                    "name": item,
                    "path": item_path,
                    "files": 0,
                    "folders": 0,
                    "size": 0
                }
                _analyze_subfolder(item_path, subfolder_info)
                subfolder_info["size_formatted"] = _format_size(subfolder_info["size"])
                info["subfolders"].append(subfolder_info)
                
    except Exception as e:
        print(f"⚠️ 分析文件夹失败 {folder_path}: {str(e)}")


def _analyze_subfolder(folder_path, info):
    """分析子文件夹"""
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


def get_detailed_file_info(file_path):
    """
    获取文件的详细信息
    :param file_path: 文件路径
    :return: 文件信息字典
    """
    try:
        stat = os.stat(file_path)
        return {
            "file_name": os.path.basename(file_path),
            "extension": os.path.splitext(file_path)[1].lower(),
            "size_bytes": stat.st_size,
            "size_formatted": _format_size(stat.st_size),
            "full_path": os.path.abspath(file_path),
            "modification_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "creation_time": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"⚠️ 获取文件信息失败 {file_path}: {str(e)}")
        return None


def get_all_files_info(folder_path, recursive=True):
    """
    获取文件夹内所有文件的详细信息
    :param folder_path: 文件夹路径
    :param recursive: 是否递归子文件夹
    :return: 文件信息列表
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"路径不是文件夹: {folder_path}")
    
    print(f"\n📁 开始获取文件详细信息: {folder_path}")
    
    files_info = []
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_info = get_detailed_file_info(file_path)
                if file_info:
                    files_info.append(file_info)
            
            if not recursive:
                break
                
    except Exception as e:
        print(f"⚠️ 获取文件列表失败 {folder_path}: {str(e)}")
    
    print(f"✅ 获取到 {len(files_info)} 个文件信息")
    return files_info


def analyze_folder_structure(folder_path, output_format="text"):
    """分析文件夹结构并输出"""
    info = get_folder_info(folder_path)
    
    if output_format == "json":
        result = json.dumps(info, ensure_ascii=False, indent=2)
        print("\n📋 文件夹分析结果 (JSON):")
        print(result)
        return result
    else:
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


def export_to_txt(folder_paths, output_path=None, recursive=True):
    """
    导出文件夹分析结果到TXT格式
    :param folder_paths: 文件夹路径列表
    :param output_path: 输出文件路径
    :param recursive: 是否递归子文件夹
    :return: 输出文件路径
    """
    if output_path is None:
        # 保存到项目的result文件夹
        result_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "result")
        # 确保result文件夹存在
        os.makedirs(result_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(result_folder, f"detailed_files_analysis_{timestamp}.txt")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for folder_path in folder_paths:
            folder_path = os.path.abspath(folder_path)
            f.write(f"\n{'=' * 60}\n")
            f.write(f"文件夹: {folder_path}\n")
            f.write(f"{'=' * 60}\n\n")
            
            files_info = get_all_files_info(folder_path, recursive)
            
            for file_info in files_info:
                f.write(f"文件名称: {file_info['file_name']}\n")
                f.write(f"文件扩展名: {file_info['extension']}\n")
                f.write(f"文件大小: {file_info['size_formatted']} ({file_info['size_bytes']} 字节)\n")
                f.write(f"文件完整路径: {file_info['full_path']}\n")
                f.write(f"文件修改时间: {file_info['modification_time']}\n")
                f.write(f"文件创建时间: {file_info['creation_time']}\n")
                f.write(f"\n{'-' * 40}\n\n")
    
    print(f"✅ TXT报告已保存到: {output_path}")
    return output_path


def export_to_csv(folder_paths, output_path=None, recursive=True):
    """
    导出文件夹分析结果到CSV格式
    :param folder_paths: 文件夹路径列表
    :param output_path: 输出文件路径
    :param recursive: 是否递归子文件夹
    :return: 输出文件路径
    """
    if output_path is None:
        # 保存到项目的result文件夹
        result_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "result")
        # 确保result文件夹存在
        os.makedirs(result_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(result_folder, f"detailed_files_analysis_{timestamp}.csv")
    
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['文件名称', '文件扩展名', '文件大小(字节)', '文件大小', '文件完整路径', '文件修改时间', '文件创建时间'])
        
        for folder_path in folder_paths:
            folder_path = os.path.abspath(folder_path)
            files_info = get_all_files_info(folder_path, recursive)
            
            for file_info in files_info:
                writer.writerow([
                    file_info['file_name'],
                    file_info['extension'],
                    file_info['size_bytes'],
                    file_info['size_formatted'],
                    file_info['full_path'],
                    file_info['modification_time'],
                    file_info['creation_time']
                ])
    
    print(f"✅ CSV报告已保存到: {output_path}")
    return output_path


def _format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
