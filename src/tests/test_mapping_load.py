# 验证映射是否正确加载
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui.components.batch_automation_panel import BatchAutomationPanel
import tkinter as tk

# 创建窗口
root = tk.Tk()
root.title("测试映射加载")
root.geometry("800x600")

# 创建面板
panel = BatchAutomationPanel(root)
panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 打印映射信息
print(f"映射表数量: {len(panel.folder_mapping)}")
print("\n前20个映射:")
for i, (name, value) in enumerate(list(panel.folder_mapping.items())[:20]):
    print(f"  {name}: {value}")

# 测试几个特定的
test_names = ["奥姑", "爱宕", "比比东", "紫府圣女", "楚宣儿"]
print("\n测试特定映射:")
for name in test_names:
    if name in panel.folder_mapping:
        print(f"  ✅ {name}: {panel.folder_mapping[name]}")
    else:
        print(f"  ❌ {name}: 未找到")

# 启动循环
print("\nGUI已启动，可以手动测试批量自动化面板功能")
root.mainloop()
