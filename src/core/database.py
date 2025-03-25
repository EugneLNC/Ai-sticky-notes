# src/core/database.py

"""
database.py
-----------
该文件用于管理应用数据存储，提供对SQLite数据库（或其他数据库）的基本操作。
可存储任务信息、完成记录、分类，以及学习时间记录等。
"""

import sqlite3
from datetime import datetime
import os
print("当前工作目录:", os.getcwd())

DB_NAME = "new_tasks.db"


class Database:
    def __init__(self, db_name: str = None):
        """
        数据库初始化，默认使用 tasks.db 作为文件名。
        如果你想使用自定义的数据库名称，可在实例化时传入 db_name 参数。
        """
        if db_name:
            self.db_name = db_name
        else:
            self.db_name = DB_NAME

        # 连接数据库并初始化
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row  # 查询结果可使用字典键名访问
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                task_type TEXT,    -- daily / monthly
                goal_type TEXT,    -- short-term / long-term
                parent_id INTEGER, -- 新增字段：关联长期任务；长期任务 parent_id 为空
                is_completed INTEGER DEFAULT 0,
                created_at TEXT,
                completed_at TEXT
            );
            """
        )
        # 保留其他表的创建...
        self.conn.commit()


        # ---------------- 学习记录表 ----------------
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,          -- 学习领域名称，如 编程, 绘画, etc
                minutes INTEGER NOT NULL,      -- 学习时间(分钟)
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        self.conn.commit()

    # =================================================================
    #                           任务操作
    # =================================================================

    def add_task(self, title: str, description: str = "",
                task_type: str = "daily", goal_type: str = "short-term", parent_id: int = None) -> int:
        cursor = self.conn.cursor()
        created_at = datetime.now().isoformat(timespec='seconds')
        cursor.execute(
            """
            INSERT INTO tasks (title, description, task_type, goal_type, parent_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (title, description, task_type, goal_type, parent_id, created_at)
        )
        self.conn.commit()
        return cursor.lastrowid


    def get_tasks(self, include_completed: bool = False) -> list:
        """
        获取所有任务，默认不包含已完成的任务
        """
        cursor = self.conn.cursor()
        if include_completed:
            cursor.execute("SELECT * FROM tasks;")
        else:
            cursor.execute("SELECT * FROM tasks WHERE is_completed=0;")

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def complete_task(self, task_id: int):
        """
        将指定id的任务标记为完成，并记录完成时间
        """
        cursor = self.conn.cursor()
        completed_at = datetime.now().isoformat(timespec='seconds')
        cursor.execute(
            """
            UPDATE tasks
            SET is_completed = 1, completed_at = ?
            WHERE id = ?;
            """,
            (completed_at, task_id)
        )
        self.conn.commit()

    def get_completed_tasks(self) -> list:
        """
        获取已完成的任务列表
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE is_completed=1;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_task(self, task_id: int):
        """
        删除指定id的任务
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
        self.conn.commit()

    def delete_completed_tasks(self):
        """
        删除所有已完成的任务记录
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE is_completed=1;")
        self.conn.commit()

    # =================================================================
    #                       学习记录(learning_log) 操作
    # =================================================================

    def add_learning_time(self, domain: str, minutes: int):
        """
        添加一条学习记录
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO learning_log (domain, minutes) VALUES (?, ?);",
            (domain, minutes)
        )
        self.conn.commit()

    def get_learning_logs(self) -> list:
        """
        按 domain 汇总总时长 (单位：分钟)
        返回示例: [ {'domain': '编程', 'total_minutes': 120}, {'domain': '绘画', 'total_minutes': 90} ]
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT domain, SUM(minutes) AS total_minutes
            FROM learning_log
            GROUP BY domain;
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    # =================================================================
    #                          关闭连接
    # =================================================================

    def close(self):
        """关闭数据库连接"""
        self.conn.close()
