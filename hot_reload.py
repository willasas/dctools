#!/usr/bin/env python3
"""
Python热重载脚本
使用watchdog库监控文件变化并自动重启应用
"""
import time
import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = None
        self.restart()
    
    def restart(self):
        """重启应用"""
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        print("\n" + "="*60)
        print("🔄 重启应用...")
        print("="*60)
        
        self.process = subprocess.Popen(self.command, shell=True)
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory:
            # 只监控Python文件
            if event.src_path.endswith('.py'):
                print(f"📁 文件修改: {event.src_path}")
                self.restart()
    
    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory:
            if event.src_path.endswith('.py'):
                print(f"📁 文件创建: {event.src_path}")
                self.restart()
    
    def on_deleted(self, event):
        """文件删除事件"""
        if not event.is_directory:
            if event.src_path.endswith('.py'):
                print(f"📁 文件删除: {event.src_path}")
                self.restart()

def main():
    """主函数"""
    # 检查watchdog库是否安装
    try:
        import watchdog
    except ImportError:
        print("❌ 缺少watchdog库，请先安装:")
        print("   pip install watchdog")
        sys.exit(1)
    
    # 默认启动命令
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
    else:
        command = 'python main.py'
    
    print("🔥 Python热重载启动器")
    print(f"📜 监控命令: {command}")
    print("👁️  监控文件变化...")
    print("💡 提示: 修改.py文件后应用会自动重启")
    print("🛑 按 Ctrl+C 退出")
    print()
    
    # 创建事件处理器
    event_handler = ChangeHandler(command)
    
    # 创建观察者
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
        print("\n👋 热重载已停止")
    
    observer.join()

if __name__ == "__main__":
    main()
