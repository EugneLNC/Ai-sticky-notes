# src/ui/main_window.py

import sys
import os

try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox, QGroupBox, QSpinBox, QFormLayout, QInputDialog
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.database import Database
from src.core.ai_service import AIService
from src.ui.task_item import TaskItem
from src.ui.pomodoro_widget import PomodoroWidget

# 定义后台线程用于调用 AI 规划
class PlanGenerationThread(QThread):
    result_ready = pyqtSignal(str)
    def __init__(self, ai_service, tasks):
        super().__init__()
        self.ai_service = ai_service
        self.tasks = tasks
    def run(self):
        try:
            plan_text = self.ai_service.generate_plan(self.tasks)
            self.result_ready.emit(plan_text)
        except Exception as e:
            self.result_ready.emit(f"发生错误: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口外观：透明、无边框、置底
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 200);")
        self.setWindowTitle("我的便签软件 - 拖动 + 壁纸模拟 + 学习记录")
        self.setMinimumSize(600, 500)

        self.dragging = False
        self.drag_position = None

        # 初始化数据库和 AI 服务（使用真实的 DeepSeek API Key）
        self.db = Database()
        self.ai_service = AIService(api_key="your api key", model="deepseek-chat")

        # 主体布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # 初始化各个 UI 区域
        self.init_task_input_area()   # 任务输入区
        self.init_task_lists_area()   # 短期 & 长期任务列表
        self.init_footer_area()       # 底部区域：已完成任务、AI规划等
        self.init_learning_area()     # 学习记录区域

        # 刷新任务列表
        self.refresh_task_lists()

        # 如果需要置于桌面背景层，可取消下面注释
        # if HAS_WIN32:
        #     from src.utils.ui_helpers import set_window_under_desktop
        #     set_window_under_desktop(self.winId())

        # 在软件启动后进行 API 测试，延迟 0 毫秒（在事件循环中执行）
        QTimer.singleShot(0, self.run_api_test)

    def run_api_test(self):
        test_result = self.ai_service.test_api()
        QMessageBox.information(None, "API 测试", f"测试结果：{test_result}")

    # ------------------- 拖动窗口相关 -------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    # ------------------- 任务输入区 -------------------
    def init_task_input_area(self):
        input_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("输入任务标题...")
        input_layout.addWidget(self.title_input)
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("任务描述(可选)...")
        input_layout.addWidget(self.desc_input)
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(["daily", "monthly"])
        input_layout.addWidget(self.task_type_combo)
        self.goal_type_combo = QComboBox()
        self.goal_type_combo.addItems(["short-term", "long-term"])
        input_layout.addWidget(self.goal_type_combo)
        add_button = QPushButton("添加任务")
        add_button.clicked.connect(self.add_task)
        input_layout.addWidget(add_button)
        self.main_layout.addLayout(input_layout)

    # ------------------- 任务列表区域 -------------------
    def init_task_lists_area(self):
        self.short_term_label = QLabel("短期目标")
        self.short_term_list = QListWidget()
        self.long_term_label = QLabel("长期目标")
        self.long_term_list = QListWidget()
        self.main_layout.addWidget(self.short_term_label)
        self.main_layout.addWidget(self.short_term_list)
        self.main_layout.addWidget(self.long_term_label)
        self.main_layout.addWidget(self.long_term_list)

    def refresh_task_lists(self):
        self.short_term_list.clear()
        self.long_term_list.clear()
        tasks = self.db.get_tasks(include_completed=False)
        for task in tasks:
            item_widget = TaskItem(task)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            item_widget.taskCompleted.connect(self.on_task_completed)
            item_widget.taskDeleted.connect(self.on_task_deleted)
            if task.get("goal_type") == "long-term":
                item_widget.generateSubTask.connect(self.on_generate_subtask)
                item_widget.viewCompletedSubTasks.connect(self.on_view_completed_subtasks)
                self.long_term_list.addItem(list_item)
                self.long_term_list.setItemWidget(list_item, item_widget)
            else:
                self.short_term_list.addItem(list_item)
                self.short_term_list.setItemWidget(list_item, item_widget)

    def add_task(self):
        try:
            title = self.title_input.text().strip()
            description = self.desc_input.text().strip()
            task_type = self.task_type_combo.currentText()
            goal_type = self.goal_type_combo.currentText()
            if not title:
                QMessageBox.warning(self, "警告", "任务标题不能为空！")
                return
            self.db.add_task(
                title=title,
                description=description,
                task_type=task_type,
                goal_type=goal_type
            )
            self.title_input.clear()
            self.desc_input.clear()
            self.refresh_task_lists()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加任务失败: {e}")

    def on_task_completed(self, task_id: int):
        self.db.complete_task(task_id)
        self.refresh_task_lists()

    def on_task_deleted(self, task_id: int):
        self.db.delete_task(task_id)
        self.refresh_task_lists()

    # ------------------- 长期任务右键操作 -------------------
    def on_generate_subtask(self, long_term_task: dict):
        default_title = long_term_task["title"] + " - 短期任务"
        title, ok = QInputDialog.getText(None, "生成短期任务", "请输入短期任务标题：", text=default_title)
        if ok and title.strip():
            description = long_term_task.get("description", "")
            self.db.add_task(
                title=title.strip(),
                description=description,
                task_type=long_term_task.get("task_type", "daily"),
                goal_type="short-term",
                parent_id=long_term_task["id"]
            )
            self.refresh_task_lists()

    def on_view_completed_subtasks(self, long_term_task: dict):
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM tasks
            WHERE parent_id = ? AND is_completed = 1;
            """,
            (long_term_task["id"],)
        )
        rows = cursor.fetchall()
        tasks = [dict(row) for row in rows]
        if tasks:
            msg = ""
            for t in tasks:
                msg += f"ID: {t['id']} | 标题: {t['title']} | 完成时间: {t['completed_at']}\n"
            QMessageBox.information(None, "完成的短期任务", msg)
        else:
            QMessageBox.information(None, "完成的短期任务", "目前没有该长期目标生成的已完成短期任务。")

    # ------------------- 底部区域：已完成任务、AI规划、删除已完成任务 -------------------
    def init_footer_area(self):
        footer_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        completed_button = QPushButton("查看已完成任务")
        completed_button.clicked.connect(self.show_completed_tasks)
        left_layout.addWidget(completed_button)
        delete_completed_button = QPushButton("删除已完成任务")
        delete_completed_button.clicked.connect(self.delete_completed_tasks)
        left_layout.addWidget(delete_completed_button)
        ai_button = QPushButton("AI规划(示例)")
        ai_button.clicked.connect(self.plan_with_ai)
        left_layout.addWidget(ai_button)
        footer_layout.addLayout(left_layout)
        from src.ui.pomodoro_widget import PomodoroWidget
        self.pomodoro_widget = PomodoroWidget()
        footer_layout.addWidget(self.pomodoro_widget)
        self.main_layout.addLayout(footer_layout)

    def show_completed_tasks(self):
        completed_tasks = self.db.get_completed_tasks()
        if not completed_tasks:
            QMessageBox.information(self, "已完成任务", "目前没有已完成任务。")
            return
        msg = ""
        for t in completed_tasks:
            msg += f"ID: {t['id']} | 标题: {t['title']} | 完成时间: {t['completed_at']}\n"
        QMessageBox.information(self, "已完成任务", msg)

    def delete_completed_tasks(self):
        confirm = QMessageBox.question(
            self, "删除确认", "确定要删除所有已完成任务吗？此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.db.delete_completed_tasks()
            QMessageBox.information(self, "提示", "已删除所有已完成任务。")
            self.refresh_task_lists()

    def plan_with_ai(self):
        tasks = self.db.get_tasks(include_completed=False)
        plan_text = self.ai_service.generate_plan(tasks)
        QMessageBox.information(None, "AI规划结果", plan_text)

    def display_plan_result(self, plan_text):
        QMessageBox.information(None, "AI规划结果", plan_text)

    # ------------------- 学习时间记录区域 -------------------
    def init_learning_area(self):
        group = QGroupBox("学习时间记录")
        layout = QVBoxLayout()
        group.setLayout(layout)
        form_layout = QFormLayout()
        self.domain_input = QLineEdit()
        form_layout.addRow("学习领域", self.domain_input)
        self.learn_minutes_spin = QSpinBox()
        self.learn_minutes_spin.setRange(1, 1440)
        self.learn_minutes_spin.setValue(30)
        self.learn_minutes_spin.setSuffix(" 分钟")
        form_layout.addRow("本次学习时长", self.learn_minutes_spin)
        layout.addLayout(form_layout)
        add_learning_btn = QPushButton("添加学习记录")
        add_learning_btn.clicked.connect(self.add_learning_record)
        layout.addWidget(add_learning_btn)
        self.learning_list = QListWidget()
        layout.addWidget(self.learning_list)
        self.refresh_learning_log()
        self.main_layout.addWidget(group)

    def add_learning_record(self):
        domain = self.domain_input.text().strip()
        minutes = self.learn_minutes_spin.value()
        if not domain:
            QMessageBox.warning(self, "提示", "请填写学习领域！")
            return
        self.db.add_learning_time(domain, minutes)
        self.refresh_learning_log()

    def refresh_learning_log(self):
        self.learning_list.clear()
        logs = self.db.get_learning_logs()
        if logs:
            for row in logs:
                domain = row["domain"]
                total_minutes = row["total_minutes"]
                item = QListWidgetItem(f"{domain}：已累计 {total_minutes} 分钟")
                self.learning_list.addItem(item)
        else:
            self.learning_list.addItem("暂无学习记录")

def main():
    print("当前工作目录:", os.getcwd())
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
