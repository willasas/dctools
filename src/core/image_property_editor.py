"""图片/视频/音频属性编辑模块"""
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCOM, TCON, TDRC, COMM
import piexif


def get_image_properties(image_path):
    """
    获取图片的属性信息
    :param image_path: 图片路径
    :return: 图片属性字典
    """
    try:
        with Image.open(image_path) as img:
            properties = {}

            # 获取基本属性
            properties['格式'] = img.format
            properties['尺寸'] = f"{img.width}x{img.height}"
            properties['模式'] = img.mode

            # 获取EXIF数据
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'GPSInfo':
                        gps_info = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_info[gps_tag] = gps_value
                        properties['GPS信息'] = gps_info
                    else:
                        properties[tag] = value

            return properties
    except Exception as e:
        print(f"⚠️ 获取图片属性失败 {image_path}: {str(e)}")
        return {}


def remove_media_properties(media_path, properties_to_remove=None, remove_all=False):
    """
    移除媒体文件的属性信息
    :param media_path: 媒体文件路径
    :param properties_to_remove: 要移除的属性列表
    :param remove_all: 是否移除所有属性
    :return: 操作结果
    """
    try:
        ext = os.path.splitext(media_path)[1].lower()

        # 处理图片文件
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
            try:
                if remove_all:
                    # 移除所有EXIF数据
                    piexif.remove(media_path)
                    print(f"✅ 成功移除图片属性: {media_path}")
                    return True
                else:
                    # 移除指定属性
                    if properties_to_remove:
                        # 加载EXIF数据
                        exif_dict = piexif.load(media_path)

                        # 确保exif_dict不是None
                        if exif_dict:
                            # 查找并移除指定属性
                            for prop in properties_to_remove:
                                # 查找属性对应的tag_id
                                tag_id = None
                                for tid, tag in TAGS.items():
                                    if tag == prop:
                                        tag_id = tid
                                        break

                                if tag_id:
                                    # 检查所有IFD并移除该tag
                                    for ifd in exif_dict:
                                        if exif_dict[ifd] and tag_id in exif_dict[ifd]:
                                            del exif_dict[ifd][tag_id]

                            # 保存修改后的EXIF数据
                            exif_bytes = piexif.dump(exif_dict)
                            with Image.open(media_path) as img:
                                img.save(media_path, exif=exif_bytes)
                            print(f"✅ 成功移除图片属性: {media_path}")
                            return True
                        else:
                            print(f"⚠️ 无法加载图片EXIF数据: {media_path}")
                            return False
                    else:
                        print(f"⚠️ 未指定要移除的属性: {media_path}")
                        return False
            except Exception as e:
                print(f"⚠️ 处理图片文件失败 {media_path}: {str(e)}")
                return False

        # 处理音频文件
        elif ext in ['.mp3', '.wav', '.flac', '.aac']:
            try:
                # 使用mutagen库移除ID3标签
                audio = mutagen.File(media_path, easy=True)
                if audio:
                    if remove_all:
                        # 移除所有标签
                        for key in list(audio.keys()):
                            del audio[key]
                    else:
                        # 移除指定标签
                        if properties_to_remove:
                            # 映射常见属性名称到ID3标签
                            id3_mapping = {
                                'Title': 'title',
                                'Artist': 'artist',
                                'Album': 'album',
                                'Composer': 'composer',
                                'Genre': 'genre',
                                'Year': 'date',
                                'Comments': 'comment'
                            }
                            for prop in properties_to_remove:
                                # 尝试使用映射的标签名
                                id3_tag = id3_mapping.get(prop, prop.lower())
                                if id3_tag in audio:
                                    del audio[id3_tag]
                                # 也尝试直接使用原始属性名
                                elif prop in audio:
                                    del audio[prop]
                    audio.save()
                    print(f"✅ 成功移除音频属性: {media_path}")
                    return True
            except Exception as e:
                print(f"⚠️ 处理音频文件失败 {media_path}: {str(e)}")
                return False

        # 处理视频文件
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
            try:
                # 首先尝试不使用easy模式
                video = mutagen.File(media_path)
                if video:
                    if remove_all:
                        # 移除所有标签
                        if hasattr(video, 'tags') and video.tags is not None:
                            for key in list(video.tags.keys()):
                                del video.tags[key]
                    else:
                        # 移除指定标签
                        if properties_to_remove and hasattr(video, 'tags') and video.tags is not None:
                            # 映射常见属性名称到标签
                            tag_mapping = {
                                'Title': 'title',
                                'Artist': 'artist',
                                'Album': 'album',
                                'Composer': 'composer',
                                'Genre': 'genre',
                                'Year': 'date',
                                'Comments': 'comment'
                            }
                            for prop in properties_to_remove:
                                # 尝试使用映射的标签名
                                tag_name = tag_mapping.get(prop, prop.lower())
                                if tag_name in video.tags:
                                    del video.tags[tag_name]
                                # 也尝试直接使用原始属性名
                                elif prop in video.tags:
                                    del video.tags[prop]
                    video.save()
                    print(f"✅ 成功移除视频属性: {media_path}")
                    return True
                else:
                    # 尝试使用easy模式
                    video_easy = mutagen.File(media_path, easy=True)
                    if video_easy:
                        if remove_all:
                            # 移除所有标签
                            for key in list(video_easy.keys()):
                                del video_easy[key]
                        else:
                            # 移除指定标签
                            if properties_to_remove:
                                # 映射常见属性名称到标签
                                tag_mapping = {
                                    'Title': 'title',
                                    'Artist': 'artist',
                                    'Album': 'album',
                                    'Composer': 'composer',
                                    'Genre': 'genre',
                                    'Year': 'date',
                                    'Comments': 'comment'
                                }
                                for prop in properties_to_remove:
                                    # 尝试使用映射的标签名
                                    tag_name = tag_mapping.get(prop, prop.lower())
                                    if tag_name in video_easy:
                                        del video_easy[tag_name]
                                    # 也尝试直接使用原始属性名
                                    elif prop in video_easy:
                                        del video_easy[prop]
                        video_easy.save()
                        print(f"✅ 成功移除视频属性: {media_path}")
                        return True
                    else:
                        print(f"⚠️ 视频文件不支持属性编辑: {media_path}")
                        return False
            except Exception as e:
                print(f"⚠️ 处理视频文件失败 {media_path}: {str(e)}")
                return False

        else:
            print(f"⚠️ 不支持的文件类型: {media_path}")
            return False
    except Exception as e:
        print(f"❌ 移除媒体属性失败 {media_path}: {str(e)}")
        return False


def add_media_property(media_path, property_name, property_value):
    """
    添加媒体文件属性
    :param media_path: 媒体文件路径
    :param property_name: 属性名称
    :param property_value: 属性值
    :return: 操作结果
    """
    try:
        ext = os.path.splitext(media_path)[1].lower()

        # 处理图片文件
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
            try:
                with Image.open(media_path) as img:
                    # 查找属性对应的tag_id
                    tag_id = None
                    for tid, tag in TAGS.items():
                        if tag == property_name:
                            tag_id = tid
                            break

                    # 特殊处理Title属性，尝试不同的tag名称和直接使用tag ID
                    if not tag_id and property_name == 'Title':
                        # 尝试其他可能的tag名称
                        for tid, tag in TAGS.items():
                            if tag in ['Object Name', 'Title', 'ImageDescription']:
                                tag_id = tid
                                break
                        # 如果仍然没有找到，直接使用ImageDescription的tag ID (270)
                        if not tag_id:
                            tag_id = 270  # ImageDescription tag ID

                    if tag_id:
                        # 使用piexif库来处理EXIF数据
                        try:
                            # 获取现有EXIF数据
                            exif_dict = piexif.load(media_path)

                            # 将属性添加到0th IFD
                            exif_dict['0th'][tag_id] = property_value

                            # 转换为字节
                            exif_bytes = piexif.dump(exif_dict)

                            # 保存图片
                            img.save(media_path, exif=exif_bytes)
                            print(f"✅ 成功添加图片属性 {property_name}: {media_path}")
                            return True
                        except Exception as e:
                            print(f"⚠️ 使用piexif添加图片属性失败 {media_path}: {str(e)}")
                            # 回退到PIL的方法
                            try:
                                exif_data = img.getexif()
                                exif_data[tag_id] = property_value
                                img.save(media_path, exif=exif_data.tobytes())
                                print(f"✅ 成功添加图片属性 {media_path}")
                                return True
                            except Exception as e2:
                                print(f"⚠️ 添加图片属性失败 {media_path}: {str(e2)}")
                                return False
                    else:
                        print(f"⚠️ 未知的属性名称: {property_name}")
                        return False
            except Exception as e:
                print(f"⚠️ 处理图片文件失败 {media_path}: {str(e)}")
                return False

        # 处理音频文件
        elif ext in ['.mp3', '.wav', '.flac', '.aac']:
            try:
                # 使用mutagen库添加ID3标签
                audio = mutagen.File(media_path, easy=True)
                if audio:
                    # 映射常见属性名称到ID3标签
                    id3_mapping = {
                        'Title': 'title',
                        'Artist': 'artist',
                        'Album': 'album',
                        'Composer': 'composer',
                        'Genre': 'genre',
                        'Year': 'date',
                        'Comments': 'comment'
                    }

                    # 获取对应的ID3标签名
                    id3_tag = id3_mapping.get(property_name, property_name.lower())

                    # 添加标签
                    audio[id3_tag] = [property_value]  # mutagen期望的是列表形式
                    audio.save()
                    print(f"✅ 成功添加音频属性 {property_name}: {media_path}")
                    return True
                else:
                    # 尝试使用ID3直接处理
                    try:
                        audio = ID3(media_path)
                        # 映射常见属性名称到ID3标签类
                        id3_tag_mapping = {
                            'Title': TIT2,
                            'Artist': TPE1,
                            'Album': TALB,
                            'Composer': TCOM,
                            'Genre': TCON,
                            'Year': TDRC,
                            'Comments': COMM
                        }

                        if property_name in id3_tag_mapping:
                            tag_class = id3_tag_mapping[property_name]
                            audio[tag_class.__name__] = tag_class(encoding=3, text=property_value)
                            audio.save()
                            print(f"✅ 成功添加音频属性 {property_name}: {media_path}")
                            return True
                        else:
                            print(f"⚠️ 不支持的音频属性: {property_name}")
                            return False
                    except Exception as e2:
                        print(f"⚠️ 处理音频文件失败 {media_path}: {str(e2)}")
                        return False
            except Exception as e:
                print(f"⚠️ 处理音频文件失败 {media_path}: {str(e)}")
                return False

        # 处理视频文件
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
            try:
                # 尝试使用mutagen库添加视频属性
                # 首先尝试不使用easy模式
                video = mutagen.File(media_path)
                if video:
                    # 对于不同类型的视频文件，尝试不同的标签设置方法
                    try:
                        # 尝试直接设置标签
                        if hasattr(video, 'tags') and video.tags is not None:
                            # 映射常见属性名称到标签
                            tag_mapping = {
                                'Title': 'title',
                                'Artist': 'artist',
                                'Album': 'album',
                                'Composer': 'composer',
                                'Genre': 'genre',
                                'Year': 'date',
                                'Comments': 'comment'
                            }

                            # 获取对应的标签名
                            tag_name = tag_mapping.get(property_name, property_name.lower())

                            # 尝试设置标签
                            video.tags[tag_name] = property_value
                            video.save()
                            print(f"✅ 成功添加视频属性 {property_name}: {media_path}")
                            return True
                        else:
                            # 尝试使用easy模式
                            video_easy = mutagen.File(media_path, easy=True)
                            if video_easy:
                                # 映射常见属性名称到标签
                                tag_mapping = {
                                    'Title': 'title',
                                    'Artist': 'artist',
                                    'Album': 'album',
                                    'Composer': 'composer',
                                    'Genre': 'genre',
                                    'Year': 'date',
                                    'Comments': 'comment'
                                }

                                # 获取对应的标签名
                                tag_name = tag_mapping.get(property_name, property_name.lower())

                                # 添加标签
                                video_easy[tag_name] = [property_value]  # mutagen期望的是列表形式
                                video_easy.save()
                                print(f"✅ 成功添加视频属性 {property_name}: {media_path}")
                                return True
                            else:
                                print(f"⚠️ 视频文件不支持属性编辑: {media_path}")
                                return False
                    except Exception as e2:
                        print(f"⚠️ 处理视频文件失败 {media_path}: {str(e2)}")
                        return False
                else:
                    print(f"⚠️ 视频文件不支持属性编辑: {media_path}")
                    return False
            except Exception as e:
                print(f"⚠️ 处理视频文件失败 {media_path}: {str(e)}")
                return False

        else:
            print(f"⚠️ 不支持的文件类型: {media_path}")
            return False
    except Exception as e:
        print(f"❌ 添加媒体属性失败 {media_path}: {str(e)}")
        return False


def batch_remove_properties(folder_path, properties_to_remove=None, remove_all=False, recursive=True):
    """
    批量移除媒体文件属性
    :param folder_path: 文件夹路径
    :param properties_to_remove: 要移除的属性列表
    :param remove_all: 是否移除所有属性
    :param recursive: 是否递归子文件夹
    :return: 操作结果
    """
    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return False

    media_extensions = [
        # 图片
        '.jpg', '.jpeg', '.png', '.bmp', '.webp',
        # 音频
        '.mp3', '.wav', '.flac', '.aac',
        # 视频
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
    ]
    processed_count = 0
    failed_count = 0

    print(f"\n📁 开始批量移除媒体属性: {folder_path}")
    print(f"   递归: {'是' if recursive else '否'}")
    print(f"   移除所有属性: {'是' if remove_all else '否'}")

    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in media_extensions:
                    file_path = os.path.join(root, file)
                    if remove_media_properties(file_path, properties_to_remove, remove_all):
                        processed_count += 1
                    else:
                        failed_count += 1
    else:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in media_extensions:
                if remove_media_properties(file_path, properties_to_remove, remove_all):
                    processed_count += 1
                else:
                    failed_count += 1

    print(f"\n✅ 批量移除媒体属性完成！")
    print(f"   成功: {processed_count} 个文件")
    print(f"   失败: {failed_count} 个文件")
    return processed_count > 0


def batch_add_property(folder_path, property_name, property_value, recursive=True):
    """
    批量添加媒体文件属性
    :param folder_path: 文件夹路径
    :param property_name: 属性名称
    :param property_value: 属性值
    :param recursive: 是否递归子文件夹
    :return: 操作结果
    """
    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return False

    media_extensions = [
        # 图片
        '.jpg', '.jpeg', '.png', '.bmp', '.webp',
        # 音频
        '.mp3', '.wav', '.flac', '.aac',
        # 视频
        '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
    ]
    processed_count = 0
    failed_count = 0

    print(f"\n📁 开始批量添加媒体属性: {folder_path}")
    print(f"   属性: {property_name} = {property_value}")
    print(f"   递归: {'是' if recursive else '否'}")

    if recursive:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in media_extensions:
                    file_path = os.path.join(root, file)
                    if add_media_property(file_path, property_name, property_value):
                        processed_count += 1
                    else:
                        failed_count += 1
    else:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path) and os.path.splitext(file)[1].lower() in media_extensions:
                if add_media_property(file_path, property_name, property_value):
                    processed_count += 1
                else:
                    failed_count += 1

    print(f"\n✅ 批量添加媒体属性完成！")
    print(f"   成功: {processed_count} 个文件")
    print(f"   失败: {failed_count} 个文件")
    return processed_count > 0
