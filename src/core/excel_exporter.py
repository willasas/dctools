"""Excel导出模块"""
import os
import pandas as pd
from datetime import datetime
from pypinyin import pinyin, Style

def get_pinyin_name(chinese_name):
    """获取中文名称的拼音"""
    if not chinese_name:
        return ""
    pinyin_result = pinyin(chinese_name, style=Style.NORMAL)
    return '_'.join([item[0] for item in pinyin_result])

def get_file_info(file_path):
    """获取文件详细信息"""
    try:
        # 确保文件路径是绝对路径且使用正确的路径分隔符
        file_path = os.path.abspath(file_path)
        
        stat = os.stat(file_path)
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        size = stat.st_size
        create_time = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
        modify_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "文件名": filename,
            "扩展名": ext,
            "大小(字节)": size,
            "大小(KB)": round(size / 1024, 2),
            "大小(MB)": round(size / (1024 * 1024), 2),
            "创建时间": create_time,
            "修改时间": modify_time,
            "文件夹": os.path.dirname(file_path),
            "路径": file_path
        }
    except Exception as e:
        # 尝试使用不同的路径处理方法
        try:
            # 尝试对路径进行编码和解码
            if isinstance(file_path, str):
                # 尝试使用utf-8编码
                file_path = file_path.encode('utf-8').decode('utf-8')
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            ext = os.path.splitext(filename)[1].lower()
            size = stat.st_size
            create_time = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            modify_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "文件名": filename,
                "扩展名": ext,
                "大小(字节)": size,
                "大小(KB)": round(size / 1024, 2),
                "大小(MB)": round(size / (1024 * 1024), 2),
                "创建时间": create_time,
                "修改时间": modify_time,
                "文件夹": os.path.dirname(file_path),
                "路径": file_path
            }
        except Exception as e2:
            print(f"⚠️ 获取文件信息失败 {file_path}: {str(e)}")
            return None

def export_to_excel(file_list, export_name="文件清单", output_dir=None):
    """
    将文件列表导出到Excel
    :param file_list: 文件路径列表
    :param export_name: 导出名称
    :param output_dir: 输出目录，默认为项目根目录下的result文件夹
    :return: 导出的文件路径
    """
    if not file_list:
        raise ValueError("文件列表为空")
    
    print(f"\n📊 开始导出Excel: {export_name}")
    print(f"   文件数量: {len(file_list)}")
    
    # 准备数据
    data = []
    for file_path in file_list:
        info = get_file_info(file_path)
        if info:
            data.append(info)
    
    if not data:
        raise ValueError("没有有效的文件信息")
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 重新排列列顺序
    columns_order = ["文件名", "扩展名", "大小(MB)", "大小(KB)", "大小(字节)", 
                    "创建时间", "修改时间", "文件夹", "路径"]
    df = df[columns_order]
    
    # 设置输出目录，默认为项目根目录下的result文件夹
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "result")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{export_name}_{timestamp}.xlsx")
    
    # 导出到Excel
    try:
        df.to_excel(output_file, index=False, engine="openpyxl")
        print(f"✅ Excel导出成功: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Excel导出失败: {str(e)}")
        raise

def batch_export_folders(folder_list, export_name="文件清单", recursive=True, include_thumbnails=False):
    """
    批量导出文件夹中的文件到Excel
    :param folder_list: 文件夹路径列表
    :param export_name: 导出名称
    :param recursive: 是否递归子文件夹
    :param include_thumbnails: 是否包含缩略图（此功能预留，当前版本未实现）
    :return: 导出的文件路径
    """
    if not folder_list:
        raise ValueError("文件夹列表为空")
    
    print(f"\n📊 开始批量导出Excel: {export_name}")
    print(f"   文件夹数量: {len(folder_list)}")
    print(f"   递归子文件夹: {'是' if recursive else '否'}")
    print(f"   包含缩略图: {'是' if include_thumbnails else '否'}")

    # 获取所有文件
    all_files = []
    for folder_path in folder_list:
        if not os.path.exists(folder_path):
            print(f"⚠️ 文件夹不存在: {folder_path}")
            continue
        
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if not file.startswith('.'):
                        all_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and not file.startswith('.'):
                    all_files.append(file_path)

    if not all_files:
        raise ValueError("没有找到任何文件")

    print(f"📊 找到 {len(all_files)} 个文件")

    # 导出到Excel
    return export_to_excel(all_files, export_name)
