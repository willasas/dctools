"""AI文件管理工具 - 主入口"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import run_gui
from src.core import (
    create_single_folder,
    batch_create_folders,
    batch_rename_files,
    preview_rename,
    remove_duplicates,
    preview_duplicates,
    get_duplicates_details,
    export_to_excel,
    batch_export_folders,
    get_folder_info,
    analyze_folder_structure
)
from src.core.image_property_editor import (
    batch_add_property,
    batch_remove_properties
)

def print_banner():
    """打印程序横幅"""
    print("=" * 80)
    print("                    AI文件管理工具 v1.0")
    print("=" * 80)
    print("功能列表:")
    print("  1. 批量创建文件夹")
    print("  2. 批量重命名文件")
    print("  3. 删除重复文件")
    print("  4. 导出Excel清单")
    print("  5. 分析文件夹信息")
    print("  6. 媒体属性编辑")
    print("  7. 启动GUI界面")
    print("  0. 退出程序")
    print("=" * 80)

def create_folders_menu():
    """文件夹创建菜单"""
    print("\n" + "=" * 80)
    print("功能1: 批量创建文件夹")
    print("=" * 80)

    # 获取父路径
    parent_path = input("请输入父文件夹路径（默认为当前目录）: ").strip()
    if not parent_path:
        parent_path = "."

    # 获取文件夹名称列表
    print("\n请输入文件夹名称列表（每行一个名称，输入空行结束）:")
    folder_names = []
    while True:
        name = input(f"文件夹 {len(folder_names) + 1}: ").strip()
        if not name:
            break
        folder_names.append(name)

    if not folder_names:
        print("❌ 未输入任何文件夹名称！")
        return

    # 创建文件夹
    print(f"\n📁 正在创建 {len(folder_names)} 个文件夹...")
    created_count = 0
    for name in folder_names:
        result = create_single_folder(name, parent_path)
        if result:
            created_count += 1

    print(f"\n✅ 成功创建 {created_count}/{len(folder_names)} 个文件夹")

def rename_files_menu():
    """文件重命名菜单"""
    print("\n" + "=" * 80)
    print("功能2: 批量重命名文件")
    print("=" * 80)

    # 获取文件夹路径
    folder_path = input("请输入文件夹路径: ").strip()
    if not folder_path:
        print("❌ 未输入文件夹路径！")
        return

    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return

    # 获取中文名称
    chinese_name = input("请输入中文名称（用于生成拼音）: ").strip()
    if not chinese_name:
        print("❌ 未输入中文名称！")
        return

    # 执行重命名
    result = batch_rename_files(folder_path, chinese_name)

    if result and "renamed" in result:
        print(f"\n✅ 成功重命名 {len(result['renamed'])} 个文件")

def remove_duplicates_menu():
    """去重菜单"""
    print("\n" + "=" * 80)
    print("功能3: 删除重复文件")
    print("=" * 80)

    # 获取文件夹路径
    folder_path = input("请输入文件夹路径: ").strip()
    if not folder_path:
        print("❌ 未输入文件夹路径！")
        return

    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return

    # 确认操作
    confirm = input(f"⚠️ 将扫描 {folder_path} 并删除重复文件，确认吗？(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return

    # 执行去重
    removed_count = remove_duplicates(folder_path)
    print(f"\n✅ 成功删除 {removed_count} 个重复文件")

def export_excel_menu():
    """Excel导出菜单"""
    print("\n" + "=" * 80)
    print("功能4: 导出文件清单到Excel")
    print("=" * 80)

    # 获取文件夹路径
    folder_path = input("请输入文件夹路径: ").strip()
    if not folder_path:
        print("❌ 未输入文件夹路径！")
        return

    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return

    # 扫描文件
    print(f"\n🔍 正在扫描文件夹: {folder_path}")
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)

    if not file_list:
        print("❌ 文件夹中没有文件！")
        return

    print(f"📊 找到 {len(file_list)} 个文件")

    # 导出Excel
    export_name = input("请输入导出名称（默认为'文件清单'）: ").strip()
    if not export_name:
        export_name = "文件清单"

    result = export_to_excel(file_list, export_name)

    if result:
        print(f"\n✅ Excel导出成功: {result}")

def analyze_folder_menu():
    """文件夹分析菜单"""
    print("\n" + "=" * 80)
    print("功能5: 分析文件夹信息")
    print("=" * 80)

    # 获取文件夹路径
    folder_path = input("请输入文件夹路径: " ).strip()
    if not folder_path:
        print("❌ 未输入文件夹路径！")
        return

    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return

    # 执行分析
    result = analyze_folder_structure(folder_path, output_format="text")
    print()

def edit_media_properties_menu():
    """媒体属性编辑菜单"""
    print("\n" + "=" * 80)
    print("功能6: 媒体属性编辑")
    print("=" * 80)

    # 获取文件夹路径
    folder_path = input("请输入文件夹路径: " ).strip()
    if not folder_path:
        print("❌ 未输入文件夹路径！")
        return

    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return

    # 选择操作
    print("\n请选择操作:")
    print("  1. 添加属性")
    print("  2. 移除属性")

    sub_choice = input("请选择操作 (1-2): " ).strip()

    if sub_choice == '1':
        # 添加属性
        property_name = input("请输入属性名称 (如 Artist, Title): " ).strip()
        if not property_name:
            print("❌ 未输入属性名称！")
            return

        property_value = input("请输入属性值: " ).strip()
        if not property_value:
            print("❌ 未输入属性值！")
            return

        # 执行添加属性
        print(f"\n📁 正在为文件夹中的媒体文件添加属性...")
        result = batch_add_property(folder_path, property_name, property_value, recursive=True)

        if result:
            print("✅ 属性添加成功！")
        else:
            print("❌ 属性添加失败！")

    elif sub_choice == '2':
        # 移除属性
        property_name = input("请输入要移除的属性名称 (如 Artist, Title): " ).strip()
        if not property_name:
            print("❌ 未输入属性名称！")
            return

        # 执行移除属性
        print(f"\n📁 正在为文件夹中的媒体文件移除属性...")
        result = batch_remove_properties(folder_path, properties_to_remove=[property_name], recursive=True)

        if result:
            print("✅ 属性移除成功！")
        else:
            print("❌ 属性移除失败！")
    else:
        print("❌ 无效选择，请重新输入！")
        return

def main():
    """主函数"""
    print_banner()

    while True:
        try:
            choice = input("\n请选择功能 (0-7): ").strip()

            if choice == '0':
                print("\n👋 感谢使用AI文件管理工具，再见！")
                break
            elif choice == '1':
                create_folders_menu()
            elif choice == '2':
                rename_files_menu()
            elif choice == '3':
                remove_duplicates_menu()
            elif choice == '4':
                export_excel_menu()
            elif choice == '5':
                analyze_folder_menu()
            elif choice == '6':
                edit_media_properties_menu()
            elif choice == '7':
                print("\n🚀 启动GUI界面...")
                run_gui()
                print_banner()
            else:
                print("❌ 无效选择，请重新输入！")

        except KeyboardInterrupt:
            print("\n\n👋 程序已中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")


if __name__ == "__main__":
    main()
