import logging
import queue
import tkinter as tk
from threading import Lock


class GUILogHandler(logging.Handler):
    """专为GUI设计的线程安全日志处理器"""

    def __init__(self, text_widget=None):
        super().__init__()
        self.text_widget = text_widget
        self.log_queue = queue.Queue()
        self.lock = Lock()
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        """将日志记录放入队列"""
        msg = self.format(record)
        with self.lock:
            self.log_queue.put(msg)

    def flush_to_widget(self):
        """将队列中的日志刷新到GUI控件"""
        while not self.log_queue.empty():
            with self.lock:
                msg = self.log_queue.get()
            if self.text_widget:
                self.text_widget.configure(state='normal')
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.configure(state='disabled')
                self.text_widget.see(tk.END)


def setup_logging(gui_handler=None):
    """配置全局日志系统"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 修复编码问题的控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    # 修复编码问题的文件处理器
    file_handler = logging.FileHandler(
        "application.log",
        encoding='utf-8',  # 明确指定UTF-8编码
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(thread)d] %(levelname)s - %(message)s")
    )

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    if gui_handler:
        logger.addHandler(gui_handler)