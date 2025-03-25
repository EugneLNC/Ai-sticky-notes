# src/utils/autostart.py

"""
autostart.py
------------
用于在Windows系统上启用/禁用开机自启动功能。
此示例使用"Startup"文件夹方式，将本程序的快捷方式复制到Startup。
若要使用注册表方式或其他方式，可自行扩展。
"""

import os
import sys
import shutil
import getpass
import subprocess

def enable_autostart(app_name: str = "MyStickyNotes", script_path: str = None):
    """
    启用软件在Windows开机自动启动（Startup文件夹）。
    
    :param app_name: 显示在快捷方式上的名称
    :param script_path: 可执行文件或脚本的绝对路径。如果为None，默认使用当前脚本路径。
    """
    if script_path is None:
        script_path = os.path.abspath(sys.argv[0])

    # Windows Startup文件夹路径
    startup_path = os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Roaming",
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup"
    )
    if not os.path.exists(startup_path):
        os.makedirs(startup_path)

    # 快捷方式名
    shortcut_name = f"{app_name}.lnk"
    shortcut_path = os.path.join(startup_path, shortcut_name)

    # 创建快捷方式
    # 方法1: 使用powershell命令创建
    # 方法2: 使用某些第三方库例如'pywin32'的win32com.shell
    # 这里采用powershell方式，以减少依赖
    powershell_script = f"""
    $WScriptShell = New-Object -ComObject WScript.Shell;
    $Shortcut = $WScriptShell.CreateShortcut('{shortcut_path}');
    $Shortcut.TargetPath = '{script_path}';
    $Shortcut.WorkingDirectory = '{os.path.dirname(script_path)}';
    $Shortcut.WindowStyle = 1;
    $Shortcut.Description = 'Start {app_name} on Windows login.';
    $Shortcut.Save();
    """
    subprocess.run(["powershell", "-Command", powershell_script], shell=True)

def disable_autostart(app_name: str = "MyStickyNotes"):
    """
    禁用软件在Windows开机自动启动（Startup文件夹）。
    
    :param app_name: 对应创建的快捷方式名称
    """
    startup_path = os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Roaming",
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup"
    )
    shortcut_path = os.path.join(startup_path, f"{app_name}.lnk")
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)

def is_autostart_enabled(app_name: str = "MyStickyNotes") -> bool:
    """
    检查是否已启用自启动。
    
    :param app_name: 快捷方式名称
    :return: True/False
    """
    startup_path = os.path.join(
        os.path.expanduser("~"),
        "AppData",
        "Roaming",
        "Microsoft",
        "Windows",
        "Start Menu",
        "Programs",
        "Startup"
    )
    shortcut_path = os.path.join(startup_path, f"{app_name}.lnk")
    return os.path.exists(shortcut_path)

if __name__ == "__main__":
    # 测试脚本
    print("示例：启用/禁用自启动")
    print("1) 启用自启动： enable_autostart('MyStickyNotes')")
    print("2) 禁用自启动： disable_autostart('MyStickyNotes')")
    print("3) 检查状态：   is_autostart_enabled('MyStickyNotes')")
