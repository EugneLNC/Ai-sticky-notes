# src/ui/pomodoro_widget.py

from PyQt5.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QPushButton
from PyQt5.QtCore import pyqtSlot
from src.utils.timer import PomodoroTimer

class PomodoroWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("番茄钟", parent)
        self.timer = PomodoroTimer()
        self.init_ui()
        self.timer.timeUpdated.connect(self.update_label)
        self.timer.timeReached.connect(self.timer_finished)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 目标时间输入
        self.time_spin = QSpinBox()
        self.time_spin.setRange(1, 600)
        self.time_spin.setValue(25)
        self.time_spin.setSuffix(" 分钟")
        layout.addWidget(self.time_spin)

        # 显示当前计时状态
        self.timer_label = QLabel("已计时: 0 秒")
        layout.addWidget(self.timer_label)

        # 按钮区：开始/暂停 和 停止
        btn_layout = QHBoxLayout()
        self.start_pause_btn = QPushButton("开始")
        self.start_pause_btn.clicked.connect(self.start_or_pause)
        btn_layout.addWidget(self.start_pause_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_timer)
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)

    @pyqtSlot()
    def start_or_pause(self):
        if not self.timer._running:
            target_seconds = self.time_spin.value() * 60
            already_used = self.timer.get_accumulated_seconds()
            if already_used >= target_seconds:
                self.timer.stop_timer()
                already_used = 0
            self.timer.start_timer(target_seconds, already_used)
            self.start_pause_btn.setText("暂停")
        else:
            self.timer.pause_timer()
            self.start_pause_btn.setText("继续")

    @pyqtSlot()
    def stop_timer(self):
        self.timer.stop_timer()
        self.timer_label.setText("已计时: 0 秒")
        self.start_pause_btn.setText("开始")

    @pyqtSlot(int)
    def update_label(self, elapsed_seconds):
        self.timer_label.setText(f"已计时: {elapsed_seconds} 秒")

    @pyqtSlot()
    def timer_finished(self):
        self.start_pause_btn.setText("开始")
