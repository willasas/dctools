"""Excel导出模块"""
import os
import pandas as pd
from datetime import datetime
from pypinyin import pinyin, Style
from src.utils.logger import get_logger

# 创建logger实例
logger = get_logger(__name__)

def get_pinyin_name(chinese_name):
    """获取中文名称的拼音"""
    if not isinstance(chinese_name, str):
        logger.warning(f"get_pinyin_name: chinese_name 必须是字符串类型，当前类型: {type(chinese_name)}")
        return ""
    if not chinese_name:
        return ""
    pinyin_result = pinyin(chinese_name, style=Style.NORMAL)
    return '_'.join([item[0] for item in pinyin_result])

def get_file_info(file_path):
    """获取文件详细信息"""
    if not isinstance(file_path, str):
        logger.warning(f"get_file_info: file_path 必须是字符串类型，当前类型: {type(file_path)}")
        return None
    if not file_path:
        logger.warning("get_file_info: file_path 不能为空")
        return None
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
                file_path = file_path.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
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
            # 更详细的错误处理
            try:
                # 尝试使用原始路径直接获取文件名
                filename = os.path.basename(file_path)
                logger.warning(f"获取文件信息失败 {file_path}: {str(e)}")
                # 只返回包含基本信息的字典，不包含错误信息
                return {
                    "文件名": filename,
                    "扩展名": "",
                    "大小(字节)": 0,
                    "大小(KB)": 0,
                    "大小(MB)": 0,
                    "创建时间": "",
                    "修改时间": "",
                    "文件夹": "",
                    "路径": file_path
                }
            except:
                logger.warning(f"获取文件信息失败 {file_path}: {str(e)}")
                return None

def export_to_excel(file_list, export_name="文件清单", output_dir=None, batch_size=1000):
    """
    将文件列表导出到Excel
    :param file_list: 文件路径列表
    :param export_name: 导出名称
    :param output_dir: 输出目录，默认为项目根目录下的result文件夹
    :param batch_size: 批处理大小，默认1000个文件一批
    :return: 导出的文件路径
    """
    if not isinstance(file_list, list):
        logger.error("export_to_excel: file_list 必须是列表类型")
        raise ValueError("file_list 必须是列表类型")
    if not file_list:
        logger.error("export_to_excel: 文件列表为空")
        raise ValueError("文件列表为空")
    if not isinstance(export_name, str):
        logger.warning(f"export_to_excel: export_name 必须是字符串类型，当前类型: {type(export_name)}")
        export_name = "文件清单"
    if output_dir is not None and not isinstance(output_dir, str):
        logger.warning(f"export_to_excel: output_dir 必须是字符串类型，当前类型: {type(output_dir)}")
        output_dir = None
    if not isinstance(batch_size, int) or batch_size <= 0:
        logger.warning(f"export_to_excel: batch_size 必须是正整数，当前值: {batch_size}，使用默认值 1000")
        batch_size = 1000

    logger.info(f"开始导出Excel: {export_name}")
    logger.info(f"文件数量: {len(file_list)}")
    logger.info(f"批处理大小: {batch_size}")

    # 准备数据
    data = []
    success_count = 0
    failed_count = 0
    total_size = 0
    file_types = {}

    total_files = len(file_list)

    # 分批处理文件
    for batch_start in range(0, total_files, batch_size):
        batch_end = min(batch_start + batch_size, total_files)
        batch_files = file_list[batch_start:batch_end]
        logger.info(f"处理批次 {batch_start+1}-{batch_end}/{total_files}")

        for i, file_path in enumerate(batch_files, batch_start + 1):
            # 显示进度
            if i % 100 == 0 or i == total_files:
                logger.info(f"进度: {i}/{total_files} ({int(i/total_files*100)}%)")

            info = get_file_info(file_path)
            if info:
                data.append(info)
                success_count += 1
                # 累计文件大小
                if "大小(字节)" in info and info["大小(字节)"]:
                    total_size += info["大小(字节)"]
                # 统计文件类型
                if "扩展名" in info and info["扩展名"]:
                    ext = info["扩展名"]
                    file_types[ext] = file_types.get(ext, 0) + 1
            else:
                failed_count += 1

    if not data:
        raise ValueError("没有有效的文件信息")

    # 创建DataFrame
    df = pd.DataFrame(data)

    # 重新排列列顺序
    columns_order = ["文件名", "扩展名", "大小(MB)", "大小(KB)", "大小(字节)",
                    "创建时间", "修改时间", "文件夹", "路径"]
    # 如果有错误信息列，添加到列顺序中
    if "错误信息" in df.columns:
        columns_order.append("错误信息")
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

        # 显示统计信息
        logger.info("导出统计:")
        logger.info(f"成功: {success_count} 个文件")
        logger.info(f"失败: {failed_count} 个文件")
        logger.info(f"总大小: {round(total_size / (1024 * 1024), 2)} MB")
        logger.info(f"文件类型: {len(file_types)} 种")
        if file_types:
            logger.info("类型分布:")
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:  # 只显示前10种类型
                logger.info(f"  {ext}: {count} 个")

        logger.info(f"Excel导出成功: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Excel导出失败: {str(e)}")
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
    if not isinstance(folder_list, list):
        logger.error("batch_export_folders: folder_list 必须是列表类型")
        raise ValueError("folder_list 必须是列表类型")
    if not folder_list:
        logger.error("batch_export_folders: 文件夹列表为空")
        raise ValueError("文件夹列表为空")
    if not isinstance(export_name, str):
        logger.warning(f"batch_export_folders: export_name 必须是字符串类型，当前类型: {type(export_name)}")
        export_name = "文件清单"
    if not isinstance(recursive, bool):
        logger.warning(f"batch_export_folders: recursive 必须是布尔类型，当前类型: {type(recursive)}")
        recursive = True
    if not isinstance(include_thumbnails, bool):
        logger.warning(f"batch_export_folders: include_thumbnails 必须是布尔类型，当前类型: {type(include_thumbnails)}")
        include_thumbnails = False

    logger.info(f"开始批量导出Excel: {export_name}")
    logger.info(f"文件夹数量: {len(folder_list)}")
    logger.info(f"递归子文件夹: {'是' if recursive else '否'}")
    logger.info(f"包含缩略图: {'是' if include_thumbnails else '否'}")

    # 获取所有文件
    all_files = []
    for folder_path in folder_list:
        if not os.path.exists(folder_path):
            logger.warning(f"文件夹不存在: {folder_path}")
            continue

        if recursive:
            for root, dirs, files in os.walk(folder_path):
                # 跳过系统缩略图目录
                if not include_thumbnails:
                    dirs[:] = [d for d in dirs if not d in ['.thumbnails', 'Thumbs.db', '.DS_Store']]

                for file in files:
                    # 跳过隐藏文件和系统缩略图文件
                    if not include_thumbnails:
                        if file.startswith('.') or file in ['Thumbs.db', '.DS_Store']:
                            continue
                    elif file.startswith('.') and file not in ['.thumbnails', 'Thumbs.db', '.DS_Store']:
                        # 如果包含缩略图，则只包含系统缩略图文件，不包含其他隐藏文件
                        continue
                    all_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    # 跳过隐藏文件和系统缩略图文件
                    if not include_thumbnails:
                        if file.startswith('.') or file in ['Thumbs.db', '.DS_Store']:
                            continue
                    elif file.startswith('.') and file not in ['.thumbnails', 'Thumbs.db', '.DS_Store']:
                        # 如果包含缩略图，则只包含系统缩略图文件，不包含其他隐藏文件
                        continue
                    all_files.append(file_path)

    if not all_files:
        raise ValueError("没有找到任何文件")

    logger.info(f"找到 {len(all_files)} 个文件")

    # 导出到Excel
    return export_to_excel(all_files, export_name)
