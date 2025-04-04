import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from core.processor import main


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.progress_var = tk.DoubleVar(value=0.0)
        self.setup_logging()  # 初始化日志系统
        self.setup_ui()

    def setup_logging(self):
        """配置日志系统，同时输出到文件和GUI"""
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # 清除现有处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # 文件日志处理器
        file_handler = logging.FileHandler("process.log", encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(file_handler)

    def setup_ui(self):
        """初始化带日志显示的GUI界面"""
        self.root.title("博主视频处理器 v1.0")
        self.root.geometry("800x600")

        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        file_frame.pack(fill=tk.X, pady=5)

        ttk.Label(file_frame, text="博主列表文件:").pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ttk.Button(file_frame, text="浏览", command=self.browse_file).pack(side=tk.LEFT)

        # 进度条区域
        progress_frame = ttk.LabelFrame(main_frame, text="处理进度", padding="10")
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X)
        self.progress_label = ttk.Label(progress_frame, text="准备就绪")
        self.progress_label.pack()

        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state='normal')
        self.log_text.tag_config('INFO', foreground='black')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('WARNING', foreground='orange')

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.run_btn = ttk.Button(
            button_frame,
            text="开始处理",
            command=self.run_processor
        )
        self.run_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="清空日志",
            command=self.clear_logs
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="退出",
            command=self.root.quit
        ).pack(side=tk.LEFT, padx=5)

        # 添加GUI日志处理器
        gui_handler = GuiLogHandler(self.log_text)
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(gui_handler)

    def browse_file(self):
        """文件选择对话框"""
        filename = filedialog.askopenfilename(
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            logging.info(f"已选择文件: {filename}")

    def clear_logs(self):
        """清空日志显示"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        logging.info("日志显示已清空")

    def update_progress(self, current, total):
        """更新进度条显示"""
        progress = (current / total) * 100
        self.progress_var.set(progress)
        self.progress_label.config(text=f"处理中: {current}/{total} ({(progress):.1f}%)")
        self.root.update_idletasks()

    def run_processor(self):
        """带进度显示的处理流程"""
        input_file = self.file_entry.get()
        if not input_file:
            messagebox.showerror("错误", "请先选择Excel文件")
            return

        # 禁用按钮防止重复点击
        self.run_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        logging.info("开始处理博主视频数据...")

        # 在子线程中运行处理任务
        import threading
        def worker():
            try:
                result = main(
                    input_file=input_file,
                    progress_callback=self.update_progress
                )
                if result:
                    logging.info("所有博主视频处理完成!")
                    self.progress_label.config(text="处理完成!")
                    messagebox.showinfo("完成", "所有博主视频处理完成!")
            except Exception as e:
                logging.error(f"处理失败: {str(e)}")
                messagebox.showerror("错误", str(e))
            finally:
                self.run_btn.config(state=tk.NORMAL)

        threading.Thread(target=worker, daemon=True).start()


class GuiLogHandler(logging.Handler):
    """自定义日志处理器，将日志输出到GUI文本框"""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text_widget.config(state='normal')
            self.text_widget.insert(tk.END, msg + "\n", record.levelname)
            self.text_widget.see(tk.END)
            self.text_widget.config(state='disabled')

        # 确保在主线程更新GUI
        if self.text_widget.winfo_exists():
            self.text_widget.after(0, append)


if __name__ == "__main__":
    app = App()
    app.root.mainloop()