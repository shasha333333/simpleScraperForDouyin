import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# ChromeDriver 路径
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")

# 常量配置
AUTHOR_LIST_FILE = "../数据收集/目标博主名单.xlsx"
STATISTICS_FILE = "../数据收集/统计数据.xlsx"
MAX_WORKERS = 6  # 并行处理的线程数

# 博主视频数据保存目录
OUTPUT_DIR = "../数据收集/统计数据"
AUTHOR_LIST_OUTPUT_DIR = "../数据收集/博主视频数据"
# 博主视频数据保存目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志配置
LOG_LEVEL = "INFO"  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(log_color)s%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}
# 反爬虫配置
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"