# src/utils/ui_helpers.py

"""
ui_helpers.py
-------------
提供一些与窗口处理相关的辅助函数，例如将窗口置于桌面背景下（壁纸效果）。
注意：该方法依赖于 pywin32，如果环境中没有安装，则无法使用。
"""

import ctypes

try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

def send_msg_to_progman():
    """
    向 Progman 发送一条消息，迫使其生成 WorkerW 窗口
    """
    if not HAS_WIN32:
        return
    progman = win32gui.FindWindow("Progman", None)
    result = ctypes.c_uint()
    win32gui.SendMessageTimeout(
        progman,
        0x052C,         # 发送的消息
        0,
        0,
        win32con.SMTO_NORMAL,
        1000,
        ctypes.byref(result)
    )

def get_workerw_handle():
    """
    枚举所有窗口，返回最后一个 WorkerW 的句柄
    """
    if not HAS_WIN32:
        return None
    workerw = []
    def callback(hwnd, lparam):
        if win32gui.GetClassName(hwnd) == "WorkerW":
            workerw.append(hwnd)
        return True
    win32gui.EnumWindows(callback, None)
    return workerw[-1] if workerw else None

def set_window_under_desktop(hwnd):
    """
    将窗口设置为桌面背景层：
    1. 向 Progman 发送消息生成 WorkerW；
    2. 获取 WorkerW 的句柄，并将 hwnd 设为其子窗口；
    3. 将窗口置于最底层。
    """
    if not HAS_WIN32:
        print("win32gui/ win32con 不可用，无法置于桌面。")
        return

    send_msg_to_progman()
    workerw = get_workerw_handle()
    if workerw:
        win32gui.SetParent(hwnd, workerw)
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_BOTTOM,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )
    else:
        print("未找到 WorkerW，无法将窗口置于桌面背景层。")
