# src/ui/task_item.py

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QCheckBox, QMenu
)
from PyQt5.QtCore import pyqtSignal, Qt

class TaskItem(QWidget):
    taskCompleted = pyqtSignal(int)
    taskDeleted = pyqtSignal(int)
    generateSubTask = pyqtSignal(dict)
    viewCompletedSubTasks = pyqtSignal(dict)

    def __init__(self, task_data: dict):
        super().__init__()
        self.task_data = task_data
        self.task_id = task_data["id"]
        self.title = task_data["title"]
        self.description = task_data.get("description", "")
        self.task_type = task_data.get("task_type", "")
        self.goal_type = task_data.get("goal_type", "")
        self.is_completed = bool(task_data.get("is_completed", 0))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        left_layout = QVBoxLayout()
        self.title_label = QLabel(self.title)
        if self.is_completed:
            self.title_label.setStyleSheet("text-decoration: line-through; color: gray;")
        left_layout.addWidget(self.title_label)
        if self.description:
            self.desc_label = QLabel(self.description)
            self.desc_label.setStyleSheet("font-size: 12px; color: #555;")
            left_layout.addWidget(self.desc_label)
        type_label = QLabel(f"类型: {self.task_type} / {self.goal_type}")
        type_label.setStyleSheet("font-size: 11px; color: #777;")
        left_layout.addWidget(type_label)
        self.layout.addLayout(left_layout)

        self.completed_checkbox = QCheckBox("完成")
        self.completed_checkbox.setChecked(self.is_completed)
        self.completed_checkbox.stateChanged.connect(self.toggle_task_completed)
        self.layout.addWidget(self.completed_checkbox)

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_task)
        self.layout.addWidget(delete_btn)

    def toggle_task_completed(self):
        if not self.is_completed:
            self.taskCompleted.emit(self.task_id)

    def delete_task(self):
        self.taskDeleted.emit(self.task_id)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            print("mousePressEvent: 右键点击")
            self.contextMenuEvent(event)
        else:
            super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        print("contextMenuEvent 触发！goal_type =", self.goal_type)
        try:
            if self.goal_type == "long-term":
                menu = QMenu(self)
                action_generate = menu.addAction("生成基于该长期目标的短期任务")
                action_view = menu.addAction("查看完成的短期任务")
                action = menu.exec_(self.mapToGlobal(event.pos()))
                if action == action_generate:
                    print("选择生成短期任务")
                    self.generateSubTask.emit(self.task_data)
                elif action == action_view:
                    print("选择查看完成的短期任务")
                    self.viewCompletedSubTasks.emit(self.task_data)
            else:
                super().contextMenuEvent(event)
        except Exception as e:
            print("右键菜单错误:", e)
