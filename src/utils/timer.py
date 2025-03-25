# src/utils/timer.py

"""
timer.py
--------
提供番茄钟等定时功能，记录某项任务的累计时间，并支持设置目标时间或闹钟提醒。
此示例基于PyQt的QTimer实现，也可使用 threading.Timer 或 asyncio 等方式。
"""

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class PomodoroTimer(QObject):
    """
    番茄钟示例类，可记录任务的累计时间、设置目标时间并进行提醒。
    使用信号来通知UI或其他逻辑当前的计时状态。
    """
    # 当计时更新时发出这个信号，包含当前已经计时的秒数
    timeUpdated = pyqtSignal(int)
    # 当目标时间达到时发出这个信号
    timeReached = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._accumulated_seconds = 0  # 当前累计的秒数
        self._target_seconds = 0       # 目标总秒数
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_timeout)
        self._timer.setInterval(1000)  # 每秒更新一次
        self._running = False

    def start_timer(self, target_seconds: int, already_used_seconds: int = 0):
        """
        开始一个新的计时。
        :param target_seconds: 目标总时长(秒)
        :param already_used_seconds: 当前已经用掉的时间(秒)，可在暂停后恢复时使用
        """
        self._target_seconds = target_seconds
        self._accumulated_seconds = already_used_seconds
        self._running = True
        self._timer.start()

    def pause_timer(self):
        """暂停计时"""
        self._running = False
        self._timer.stop()

    def resume_timer(self):
        """继续计时"""
        if not self._running:
            self._running = True
            self._timer.start()

    def stop_timer(self):
        """停止计时，并重置所有数据"""
        self._running = False
        self._timer.stop()
        self._accumulated_seconds = 0
        self._target_seconds = 0

    def _on_timeout(self):
        """
        每秒触发一次，累计时间+1，若达目标则发出信号
        """
        if self._running:
            self._accumulated_seconds += 1
            self.timeUpdated.emit(self._accumulated_seconds)
            if self._target_seconds > 0 and self._accumulated_seconds >= self._target_seconds:
                self.timeReached.emit()
                # 可在此自动停止或自行决定
                self.pause_timer()

    def get_accumulated_seconds(self):
        """返回当前已累计的秒数"""
        return self._accumulated_seconds

    def get_target_seconds(self):
        """返回当前目标的总秒数"""
        return self._target_seconds
