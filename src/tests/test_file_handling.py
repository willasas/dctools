"""测试文件处理问题"""
import os
from PIL import Image
import mutagen

# 测试文件处理
test_files = [
    "E:/AI玲珑/ts\Beyond - 不再犹豫【凯霖资源】.mp3",
    "E:/AI玲珑/ts\pic_ai_ake_2025101400001.jpg",
    "E:/AI玲珑/ts\八重神子.mp4"
]

print("测试文件处理...")

for file_path in test_files:
    print(f"\n测试文件: {file_path}")
    print(f"文件是否存在: {os.path.exists(file_path)}")
    print(f"文件是否可写: {os.access(file_path, os.W_OK)}")
    
    # 测试文件打开和保存
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
            print("测试图片文件...")
            with Image.open(file_path) as img:
                print(f"图片格式: {img.format}")
                print(f"图片尺寸: {img.width}x{img.height}")
                # 尝试保存
                temp_path = file_path + ".temp"
                img.save(temp_path)
                print(f"成功保存到临时文件: {temp_path}")
                os.remove(temp_path)
                print("成功删除临时文件")
        
        elif ext in ['.mp3', '.wav', '.flac', '.aac']:
            print("测试音频文件...")
            audio = mutagen.File(file_path, easy=True)
            if audio:
                print(f"音频格式: {audio.info}")
                # 尝试保存
                audio.save()
                print("成功保存音频文件")
        
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
            print("测试视频文件...")
            video = mutagen.File(file_path)
            if video:
                print(f"视频格式: {video.info}")
                # 尝试保存
                video.save()
                print("成功保存视频文件")
    
    except Exception as e:
        print(f"错误: {str(e)}")
