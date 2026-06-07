"""文件夹创建模块"""
import os
from pypinyin import pinyin, Style
from src.utils.logger import get_logger

# 创建logger实例
logger = get_logger(__name__)

def get_chinese_initial(chinese_name):
    """获取中文名称的首字母大写"""
    if not chinese_name or not isinstance(chinese_name, str):
        logger.warning(f"get_chinese_initial: chinese_name 必须是非空字符串，当前值: {chinese_name}")
        return ""

    try:
        first_char = chinese_name[0]
        pinyin_result = pinyin(first_char, style=Style.FIRST_LETTER)
        if pinyin_result and pinyin_result[0]:
            return pinyin_result[0][0].upper()

        return ""
    except Exception as e:
        logger.warning(f"获取中文首字母失败: {str(e)}")
        return ""

def create_single_folder(chinese_name, parent_path=".", use_initial_naming=True):
    """
    创建单个文件夹（使用首字母命名规则）
    :param chinese_name: 中文名称
    :param parent_path: 父路径
    :param use_initial_naming: 是否使用首字母命名规则
    :return: 文件夹路径
    """
    # 参数验证
    if not isinstance(chinese_name, str):
        logger.error("create_single_folder: chinese_name 必须是字符串类型")
        return None
    if not chinese_name:
        logger.error("create_single_folder: chinese_name 不能为空")
        return None
    if not isinstance(parent_path, str):
        logger.error("create_single_folder: parent_path 必须是字符串类型")
        return None
    if not isinstance(use_initial_naming, bool):
        logger.warning(f"create_single_folder: use_initial_naming 必须是布尔类型，当前类型: {type(use_initial_naming)}")
        use_initial_naming = True

    try:
        # 确保父路径存在
        if not os.path.exists(parent_path):
            try:
                os.makedirs(parent_path, exist_ok=True)
                logger.info(f"创建父路径: {parent_path}")
            except Exception as e:
                logger.error(f"创建父路径失败: {str(e)}")
                return None

        # 根据参数决定是否使用首字母命名规则
        if use_initial_naming:
            initial = get_chinese_initial(chinese_name)
            folder_name = f"{initial}_{chinese_name}" if initial else chinese_name
        else:
            folder_name = chinese_name

        # 检查文件夹名称是否包含无效字符
        invalid_chars = '<>:"/\\|?*'
        if any(char in folder_name for char in invalid_chars):
            logger.error(f"文件夹名称包含无效字符: {folder_name}")
            return None

        folder_path = os.path.join(parent_path, folder_name)

        # 创建文件夹
        try:
            os.makedirs(folder_path, exist_ok=True)
            logger.info(f"创建文件夹: {folder_path}")
            return folder_path
        except PermissionError:
            logger.error(f"权限不足，无法创建文件夹: {folder_path}")
            return None
        except OSError as e:
            logger.error(f"创建文件夹失败: {str(e)}")
            return None

    except Exception as e:
        logger.error(f"创建文件夹时发生未知错误: {str(e)}")
        return None

def batch_create_folders(folder_list, use_initial_naming=True):
    """
    批量创建文件夹
    :param folder_list: 文件夹信息列表
    :param use_initial_naming: 是否使用首字母命名规则
    :return: 创建成功的文件夹路径列表
    """
    # 参数验证
    if not isinstance(folder_list, list):
        logger.error("batch_create_folders: folder_list 必须是列表类型")
        return []
    if not isinstance(use_initial_naming, bool):
        logger.warning(f"batch_create_folders: use_initial_naming 必须是布尔类型，当前类型: {type(use_initial_naming)}")
        use_initial_naming = True

    created_folders = []
    total = len(folder_list)

    for i, folder_info in enumerate(folder_list, 1):
        try:
            if not isinstance(folder_info, dict):
                logger.warning(f"第 {i} 个文件夹信息不是字典类型: {folder_info}")
                continue

            name = folder_info.get("name", "")
            path = folder_info.get("path", ".")

            if not name:
                logger.warning(f"第 {i} 个文件夹名称为空")
                continue

            folder_path = create_single_folder(name, path, use_initial_naming)
            if folder_path:
                created_folders.append(folder_path)

            # 显示进度
            if i % 10 == 0 or i == total:
                logger.info(f"创建进度: {i}/{total}")

        except Exception as e:
            logger.error(f"处理第 {i} 个文件夹时发生错误: {str(e)}")
            continue

    logger.info(f"批量创建完成，成功: {len(created_folders)}/{total}")
    return created_folders
