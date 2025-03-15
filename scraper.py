from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time



# 指定 ChromeDriver 路径
chrome_driver_path = r'D:\Anaconda3\chromedriver-win64\chromedriver.exe'

# 创建Chrome选项
options = Options()
# 添加反爬虫检测绕过设置
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# 设置更真实的用户代理
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
options.add_argument(f'user-agent={user_agent}')
options.ignore_local_proxy_environment_variables()

# 创建 WebDriver 实例
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# 打开抖音首页
driver.get("https://www.douyin.com")

# 初始化 WebDriverWait
wait = WebDriverWait(driver, 10)

print("关闭按钮...")
try:
    # 先定位固定兄弟元素（通过文字内容）
    fixed_sibling = wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "登录后免费畅享高清视频")]'))
    )

    # 通过 XPath 定位关闭按钮（假设关闭按钮是固定兄弟元素的下一个兄弟）
    close_button = fixed_sibling.find_element(By.XPATH, './following-sibling::div')

    # 点击关闭按钮
    close_button.click()
    print("关闭按钮已点击")
except TimeoutException:
    print("未找到固定兄弟元素")
except NoSuchElementException:
    print("关闭按钮未找到")

# 目标博主名称
target_author = "123"  # 替换为你要搜索的博主名称

# 动作链：搜索目标博主并进入其主页
try:
    # 1. 点击搜索按钮
    search_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-e2e="searchbar-input"]'))
    )
    ActionChains(driver).move_to_element(search_button).click().perform()
    print("已点击搜索按钮")

    # 2. 输入目标博主名称
    search_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-e2e="searchbar-input"]'))
    )
    ActionChains(driver).move_to_element(search_input).click().send_keys(target_author,Keys.ENTER).perform()
    print(f"已输入博主名称: {target_author}")


    # 3. 等待搜索结果加载
    time.sleep(5)  # 根据实际情况调整等待时间

    # 4. 点击“用户”按钮
    user_tab = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="search-content-area"]/div/div[1]/div[1]/div[1]/div[1]/div/span[3]'))
    )
    ActionChains(driver).move_to_element(user_tab).click().perform()
    print("已点击用户按钮")

    # 5. 等待用户结果加载
    time.sleep(5)  # 根据实际情况调整等待时间

    # 5. 从搜索结果中选择目标博主
    try:
        # 假设目标博主是第一个搜索结果
        author_element = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "user-info")]/a'))
        )
        ActionChains(driver).move_to_element(author_element).click().perform()
        print("已点击目标博主")

        # 6. 等待博主主页加载
        time.sleep(5)  # 根据实际情况调整等待时间

        # 打印当前URL（博主主页）
        print(f"成功进入博主主页: {driver.current_url}")
    except (TimeoutException, NoSuchElementException):
        print("未找到目标博主")
except (TimeoutException, NoSuchElementException) as e:
    print(f"操作失败: {e}")
finally:
    # 关闭浏览器
    driver.quit()