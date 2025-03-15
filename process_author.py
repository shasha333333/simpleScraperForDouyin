from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import logging
import os
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ChromeDriver 路径
CHROME_DRIVER_PATH = r'D:\Anaconda3\chromedriver-win64\chromedriver.exe'

# 博主视频数据保存目录
OUTPUT_DIR = "./博主视频数据"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def init_driver():
    """初始化 WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # 减少内存占用
    chrome_options.add_argument("--disable-extensions")  # 禁用扩展
    chrome_options.add_argument("--disable-images")  # 不加载图片，提高速度
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-javascript")  # 根据需要可以禁用JavaScript
    chrome_options.add_argument("--incognito")  # 无痕模式
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.ignore_local_proxy_environment_variables()

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def close_window(wait):
    """关闭登录弹窗"""
    logging.info("尝试关闭登录弹窗...")
    try:
        fixed_sibling = wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "登录后免费畅享高清视频")]'))
        )
        close_button = fixed_sibling.find_element(By.XPATH, './following-sibling::div')
        close_button.click()
        logging.info("登录弹窗已关闭")
    except TimeoutException:
        logging.warning("未找到登录弹窗")
    except NoSuchElementException:
        logging.warning("关闭按钮未找到")


def extract_video_info(video):
    """从单个视频元素中提取信息"""
    try:
        title_element = video.find_element(By.XPATH, './/a//p')
        title = title_element.text.strip() or title_element.get_attribute("innerText") or title_element.get_attribute(
            "textContent")
        like_count = video.find_element(By.XPATH, './/span').text.strip()
        video_link = video.find_element(By.XPATH, './/a').get_attribute("href")
        return {
            "标题": title,
            "点赞数": like_count,
            "链接": video_link
        }
    except NoSuchElementException:
        logging.warning("视频信息提取失败，跳过该视频")
        return None


def get_author_info(author_url):
    """获取博主信息并保存视频数据"""
    driver = init_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(author_url)
        close_window(wait)

        # 提取博主名字
        author_info = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-e2e="user-info"]')))
        author_name = author_info.find_element(By.XPATH, './/span').text.strip()
        logging.info(f"博主名字: {author_name}")

        # 提取视频列表
        post_list = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-e2e="user-post-list"]')))
        video_list = post_list.find_element(By.XPATH, './/ul')
        videos = video_list.find_elements(By.XPATH, './/li')

        # 提取视频信息
        video_data = []
        for video in videos:
            video_info = extract_video_info(video)
            if video_info:
                video_data.append(video_info)
                logging.info(f"提取到视频: {video_info['标题']}")

        # 保存到 Excel 文件
        if video_data:
            excel_filename = os.path.join(OUTPUT_DIR, f"{author_name}_抖音视频信息.xlsx")
            df = pd.DataFrame(video_data)
            df.to_excel(excel_filename, index=False, engine="openpyxl")
            logging.info(f"视频信息已保存到 {excel_filename}")
            return excel_filename
        else:
            logging.warning("未提取到视频信息，未生成 Excel 文件")
            return None

    except TimeoutException:
        logging.error("页面加载超时，未找到目标元素")
    except NoSuchElementException:
        logging.error("目标元素未找到")
    except Exception as e:
        logging.error(f"发生未知错误: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    time_start = time.time()  # 开始计时
    # 替换为你要爬取的抖音博主 URL
    author_url = "https://www.douyin.com/user/MS4wLjABAAAAe7E39khw8gf387YKAoQ6jxOnPLeIJH5ntk9GUhFGWPbBd4WHJo_bkJiuk1PYzz6l?from_tab_name=main"

    logging.info("开始爬取视频信息...")
    get_author_info(author_url)

    time_end = time.time()  # 结束计时
    time_c = time_end - time_start  # 运行所花时间
    logging.info(f"总计花费{time_c}秒")