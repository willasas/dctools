"""测试路径替换问题"""
import os

# 测试路径处理
test_path = "E:/AI玲珑/ts"

print(f"原始路径: {test_path}")
print(f"路径是否存在: {os.path.exists(test_path)}")

# 测试os.walk
print("\n测试os.walk:")
for root, dirs, files in os.walk(test_path):
    print(f"root: {root}")
    for file in files:
        file_path = os.path.join(root, file)
        print(f"file_path: {file_path}")
        # 检查路径中是否有'tts'
        if 'tts' in file_path:
            print(f"⚠️ 路径中包含'tts': {file_path}")

# 测试字符串替换
print("\n测试字符串替换:")
test_string = "E:/AI玲珑/ts/pic_ai_ake_2025101400001.jpg"
print(f"原始字符串: {test_string}")
print(f"替换'ts'为'tts': {test_string.replace('ts', 'tts')}")
