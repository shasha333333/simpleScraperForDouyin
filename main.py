import pandas as pd
import logging
import time
from pathlib import Path
from functools import wraps
from read_author import read_author_urls_from_excel
import process_author
import process_video
import concurrent.futures

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("process.log"),
        logging.StreamHandler()
    ]
)

# 常量配置
AUTHOR_LIST_FILE = "目标博主名单.xlsx"
STATISTICS_FILE = "统计数据.xlsx"
MAX_WORKERS = 4  # 并行处理的线程数


def timer_decorator(func):
    """计时器装饰器，用于记录函数执行时间"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"{func.__name__} 执行完成，花费 {elapsed_time:.2f} 秒")
        return result

    return wrapper


def safe_read_excel(file_path):
    """安全读取Excel文件"""
    try:
        if Path(file_path).exists():
            return pd.read_excel(file_path)
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"读取Excel文件 {file_path} 失败: {e}")
        return pd.DataFrame()


def save_to_excel(df, file_path):
    """安全保存数据到Excel文件"""
    try:
        df.to_excel(file_path, index=False)
        logging.info(f"数据已保存到 {file_path}")
        return True
    except Exception as e:
        logging.error(f"保存数据到 {file_path} 失败: {e}")
        return False


@timer_decorator
def process_author_videos(author_url):
    """
    处理单个博主的所有视频，提取点赞数最高的视频信息并保存到Excel文件

    :param author_url: 博主主页URL
    :return: 获取的视频信息或None
    """
    try:
        # 获取博主信息并保存视频数据
        excel_filename = process_author.get_author_info(author_url)

        if not excel_filename:
            logging.warning(f"未找到博主 {author_url} 的视频信息")
            return None

        # 读取视频数据并找出最受欢迎的视频
        df = safe_read_excel(excel_filename)
        if df.empty:
            logging.warning(f"博主 {author_url} 的视频数据为空")
            return None

        # 将点赞数列转换为数值类型
        df["点赞数"] = pd.to_numeric(df["点赞数"], errors="coerce")

        # 检查是否有有效的点赞数据
        if df["点赞数"].isna().all():
            logging.warning(f"博主 {author_url} 的视频没有有效的点赞数据")
            return None

        # 选择点赞数最高的视频
        most_liked_video = df.loc[df["点赞数"].idxmax()]
        video_link = most_liked_video["链接"]
        logging.info(f"博主 {author_url} 点赞数最高的视频链接: {video_link}")

        # 获取视频信息
        video_info = process_video.get_video_info(video_link)

        if not video_info:
            logging.warning(f"未能获取视频 {video_link} 的信息")
            return None

        # 添加博主URL以便追踪
        video_info["博主URL"] = author_url

        # 打印视频信息摘要
        logging.info(f"获取到视频信息: 标题={video_info.get('标题', 'N/A')}, 点赞={video_info.get('点赞数', 'N/A')}")

        return video_info

    except Exception as e:
        logging.error(f"处理博主 {author_url} 时发生错误: {str(e)}")
        return None


def update_statistics_file(video_info_list):
    """更新统计数据文件"""
    if not video_info_list:
        logging.warning("没有有效的视频信息需要保存")
        return False

    # 过滤None值
    valid_info = [info for info in video_info_list if info is not None]
    if not valid_info:
        logging.warning("所有视频信息获取失败")
        return False

    # 将新数据转换为DataFrame
    new_data = pd.DataFrame(valid_info)

    # 读取现有数据并合并
    existing_data = safe_read_excel(STATISTICS_FILE)
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)

    # 去除可能的重复数据
    if "链接" in updated_data.columns:
        updated_data.drop_duplicates(subset=["链接"], keep="last", inplace=True)

    # 保存更新后的数据
    return save_to_excel(updated_data, STATISTICS_FILE)


@timer_decorator
def main():
    """主函数，处理所有博主的视频信息"""
    try:
        # 确保输出目录存在
        Path(STATISTICS_FILE).parent.mkdir(parents=True, exist_ok=True)

        # 读取博主URL列表
        author_urls = read_author_urls_from_excel(AUTHOR_LIST_FILE)
        if not author_urls:
            logging.warning(f"未从 {AUTHOR_LIST_FILE} 中读取到博主URL")
            return

        logging.info(f"开始处理 {len(author_urls)} 个博主...")

        # 使用线程池并行处理博主
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            video_info_list = list(executor.map(process_author_videos, author_urls))

        # 更新统计数据文件
        if update_statistics_file(video_info_list):
            logging.info(f"成功更新统计数据文件 {STATISTICS_FILE}")
        else:
            logging.error("更新统计数据文件失败")

        # 统计成功和失败的数量
        success_count = sum(1 for info in video_info_list if info is not None)
        logging.info(f"处理完成: 成功 {success_count}/{len(author_urls)} 个博主")

    except Exception as e:
        logging.error(f"主函数执行时发生错误: {str(e)}")


if __name__ == "__main__":
    logging.info("=" * 50)
    logging.info("开始处理博主视频信息...")
    main()
    logging.info("处理完成!")
    logging.info("=" * 50)