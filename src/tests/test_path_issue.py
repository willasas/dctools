"""测试路径处理问题"""
import os

# 测试路径处理
test_path = "E:/AI玲珑/ts"

print(f"测试文件夹路径: {test_path}")
print(f"文件夹是否存在: {os.path.exists(test_path)}")

# 测试递归遍历
if os.path.exists(test_path):
    print("\n递归遍历文件:")
    for root, dirs, files in os.walk(test_path):
        print(f"\n当前目录: {root}")
        print(f"子目录: {dirs}")
        for file in files:
            file_path = os.path.join(root, file)
            print(f"文件: {file_path}")
            print(f"文件是否可写: {os.access(file_path, os.W_OK)}")
