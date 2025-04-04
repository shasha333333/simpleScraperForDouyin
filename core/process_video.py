from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import logging
import time

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ChromeDriver 路径
CHROME_DRIVER_PATH = r'D:\Anaconda3\chromedriver-win64\chromedriver.exe'


def init_driver():
    """初始化 WebDriver"""
    options = Options()
    options.add_argument("--headless")  # 无头模式，不打开浏览器窗口
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # 减少内存占用
    options.add_argument("--disable-extensions")  # 禁用扩展
    options.add_argument("--disable-images")  # 不加载图片，提高速度
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("--disable-javascript")  # 根据需要可以禁用JavaScript
    options.add_argument("--incognito")  # 无痕模式
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")

    # 设置更真实的用户代理
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')

    # 忽略代理设置
    options.ignore_local_proxy_environment_variables()

    # 创建 Service 对象和 WebDriver
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    # 执行 CDP 命令来避免被检测
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
    })

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


def extract_video_info(wait):
    """提取视频信息"""
    video_info = {}

    # 获取点赞数
    logging.info("开始爬取点赞数...")
    try:
        like_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="douyin-right-container"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[1]/div[1]/span')
            )
        )
        video_info['点赞量'] = like_element.text.strip()
    except (TimeoutException, NoSuchElementException):
        video_info['点赞量'] = "无法获取点赞数"

    # 获取评论数
    logging.info("开始爬取评论数...")
    try:
        comment_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="douyin-right-container"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[1]/div[2]/span')
            )
        )
        video_info['评论量'] = comment_element.text.strip()
    except (TimeoutException, NoSuchElementException):
        video_info['评论量'] = "无法获取评论数"

    # 获取转发数
    logging.info("开始爬取转发数...")
    try:
        share_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="douyin-right-container"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[1]/div[3]/span')
            )
        )
        video_info['转发量'] = share_element.text.strip()
    except (TimeoutException, NoSuchElementException):
        video_info['转发量'] = "无法获取转发数"

    # 获取视频标题
    logging.info("开始爬取视频标题...")
    try:
        title_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="douyin-right-container"]/div[2]/div/div/div[1]/div[3]/div/div[1]')
            )
        )
        video_info['标题'] = title_element.text.strip()
    except (TimeoutException, NoSuchElementException):
        video_info['标题'] = "无法获取视频标题"

    # 获取作者信息
    logging.info("开始爬取作者信息...")
    try:
        author_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="douyin-right-container"]/div[2]/div/div/div[2]/div/div[1]/div[2]/a/div/span/span/span/span/span/span')
            )
        )
        video_info['博主'] = author_element.text.strip()
    except (TimeoutException, NoSuchElementException):
        video_info['博主'] = "无法获取作者信息"

    # 获取视频发布日期
    logging.info("开始爬取发布日期...")
    try:
        date_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="douyin-right-container"]/div[2]/div/div/div[1]/div[3]/div/div[2]/div[2]')
            )
        )
        full_text = date_element.text.strip()
        time_match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", full_text)
        if time_match:
            video_info['发布日期'] = time_match.group(0)
    except (TimeoutException, NoSuchElementException):
        video_info['发布日期'] = "无法获取发布日期"

    return video_info


def get_video_info(video_url):
    """获取视频信息"""
    driver = init_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(video_url)
        # close_window(wait)

        # 提取视频信息
        video_info = extract_video_info(wait)
        return video_info

    except Exception as e:
        logging.error(f"爬取过程中发生错误: {e}")
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    time_start = time.time()  # 开始计时

    # 替换为你要爬取的抖音视频 URL
    video_url = "https://www.douyin.com/video/7481670454600600842"  # 注意：确保ID是正确的

    logging.info("开始爬取视频信息...")
    video_info = get_video_info(video_url)



    if video_info:
        logging.info("\n获取到的视频信息:")
        for key, value in video_info.items():
            logging.info(f"{key}: {value}")
    else:
        logging.error("未能获取视频信息，请检查URL或网络连接。")


    time_end = time.time()  # 结束计时
    time_c = time_end - time_start  # 运行所花时间
    logging.info(f"总计花费{time_c}秒")