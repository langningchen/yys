# Copyright (C) 2025 Langning Chen
#
# This file is part of yys.
#
# yys is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# yys is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with yys.  If not, see <https://www.gnu.org/licenses/>.

import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options as ChromeOptions

import time
import re

CHANNEL = "fast"
# CHANNEL = "normal"

def initialize_browser():
    print("Initializing browser...")
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)


def set_cookie(driver, token):
    print("Setting up browser options...")
    driver.get("https://ys.mihoyo.com/cloud")
    driver.delete_all_cookies()
    driver.add_cookie(
        {
            "name": "uni_web_token",
            "value": token,
            "path": "/",
            "domain": ".mihoyo.com",
            "secure": True,
            "httpOnly": True,
            "sameSite": "None",
        }
    )
    print("Cookie set, refreshing page...")
    driver.refresh()


def wait_for_login_status(driver):
    print("Waiting for login status...")
    try:
        WebDriverWait(driver, 30).until(
            lambda d: d.find_element(
                By.CLASS_NAME, "welcome-wrapper__has-login"
            ).is_displayed()
        )
    except Exception as e:
        raise RuntimeError(
            "Login status check failed: logged-in interface not detected, please check the token"
        ) from e


def wait_for_daily_reward(driver):
    print("Login status confirmed, waiting for daily login reward...")
    try:
        WebDriverWait(driver, 30).until(lambda d: "每日登陆奖励" in d.page_source)
        return True # 找到了
    except Exception as e:
        print("Daily login reward not found, 也许领过了")
        return False  # 没找到


def take_screenshot(driver, filename):
    # print("Daily login reward found, taking screenshot...")
    for element in driver.find_elements(By.CLASS_NAME, "van-overlay"):
        driver.execute_script("arguments[0].remove();", element)
    driver.save_screenshot(filename)

from selenium.webdriver.support import expected_conditions as EC

def enter_game(driver):
    print("正在点击进入游戏")
    try:
        time.sleep(1)
        btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), '进入游戏')]")
            )
        )
        btn.click()

        # btn = WebDriverWait(driver, 30).until(
        #     EC.presence_of_element_located(
        #         (By.XPATH, "//div[contains(@class,'wel-card__content--start') and contains(., '进入游戏')]")
        #     )
        # )
        # driver.execute_script("arguments[0].click();", btn) # 强制触发

    except Exception as e:
        print(f"未找到“进入游戏”按钮: {e}")
        return False
    return True


def choose_channel(driver, minutes=1):
    """
    根据 CHANNEL 选择对应的队列 div，记录等待时间，点击并等待进入游戏按钮。
    每个 DOM 元素查找都使用显式等待，最大等待时间 60 秒。

    :param driver: selenium webdriver 实例
    :param CHANNEL: "fast" 或 "normal"
    :param minutes: 等待时间额外增加的分钟数
    :return: True 如果成功点击进入游戏按钮，False 超时未找到
    """
    print(f"正在选择{CHANNEL}通道")

    # 目标队列文本
    target_text_map = {
        "fast": "原点快速队列",
        "normal": "普通队列"
    }
    target_text = target_text_map.get(CHANNEL)
    if not target_text:
        raise ValueError(f"未知 CHANNEL: {CHANNEL}")

    target_item = None
    wait_seconds = 15  # 默认等待时间

    # 1️⃣ 等待并找到所有排队选项
    try:
        choose_items = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.coin-prior-choose-item.coin-prior-choose-item-include-info.choose-item")
            )
        )
    except Exception:
        print("超时 60 秒未找到任何排队选项")
        return False

    # 2️⃣ 找到对应 div 并解析预计等待时间
    for item in choose_items:
        try:
            main_text_el = WebDriverWait(item, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".coin-prior-choose-item-main__desc__main"))
            )
            if main_text_el.text.strip() == target_text:
                target_item = item

                # 获取等待时间元素
                time_el = WebDriverWait(item, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".coin-prior-choose-item-info__time"))
                )
                time_text = time_el.text.strip()

                # 提取数字
                match = re.search(r"(\d+)", time_text)
                if match:
                    value = int(match.group(1))
                    if "秒" in time_text:
                        wait_seconds = value
                    elif "分钟" in time_text:
                        wait_seconds = value * 60
                break
        except Exception:
            continue
    
    print(f"{CHANNEL}通道预计等待{wait_seconds}s")

    if not target_item:
        print(f"未找到 {CHANNEL} 队列选项")
        return False

    # 3️⃣ 点击目标 div
    try:
        clickable_item = WebDriverWait(target_item, 60).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".coin-prior-choose-item-main__desc__main"))
        )
        clickable_item.click()
    except Exception:
        print(f"超时 60 秒无法点击 {CHANNEL} 队列选项")
        return False

    # 4️⃣ 等待“进入游戏”按钮出现
    total_wait = wait_seconds + minutes * 60
    try:
        enter_btn = WebDriverWait(driver, total_wait).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[starts-with(normalize-space(.), '进入游戏(') or starts-with(normalize-space(.), '进入游戏（')]"
            ))
        )
        # 5️⃣ 点击按钮
        enter_btn.click()
        print("已点击进入游戏（第二步）按钮")
        return True
    except Exception:
        print(f"超时 {total_wait} 秒未找到进入游戏按钮")
        return False


def click_accept(driver):
    print("正在点击接受按钮")
    try:
        accept_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='接受']/ancestor::button")
            )
        )
        accept_btn.click()
        print("点击“接受”按钮成功")
        return True
    except Exception as e:
        print(f"未找到“接受”按钮，可能已经接受过: {e}")
        return False

import time
from selenium.webdriver.common.action_chains import ActionChains

def click_center_x10(driver):
    print("正在点击video中央")
    size = driver.get_window_size()
    x = size['width'] // 2
    y = size['height'] // 2

    actions = ActionChains(driver)
    for i in range(10):  # 改为10次
        try:
            actions.move_by_offset(x, y).click().perform()
            print(f"video点击 {i + 1} 次完成")
            # 点击后复位偏移
            actions.move_by_offset(-x, -y)
            if i < 9:
                time.sleep(5)  # 改为每次间隔5秒
        except Exception as e:
            print(f"video点击第 {i + 1} 次失败: {e}")


from selenium.webdriver.common.keys import Keys
import random


def confuse(driver):
    actions = ActionChains(driver)
    try:
        actions.send_keys('b').perform()
        print("键盘输入 'b' 完成")
        wait_seconds = random.randint(1, 30)
        print(f"等待 {wait_seconds} 秒后输入 'Esc'")
        time.sleep(wait_seconds)
        actions.send_keys(Keys.ESCAPE).perform()
        print("键盘输入 'Esc' 完成")
    except Exception as e:
        print(f"键盘输入失败: {e}")

def take_domshot(driver, filename):
    try:
        dom = driver.page_source  # 获取完整 HTML（当前 DOM 状态）

        with open(filename, "w", encoding="utf-8") as f:
            f.write(dom)

        print(f"[DOMSHOT] Saved DOM to {filename}")
    except Exception as e:
        print(f"[DOMSHOT ERROR] {e}")

def close_save_website_ad(driver, timeout=5):
    """
    等待页面上出现弹窗的关闭按钮，并点击它。
    
    driver: Selenium WebDriver 实例
    timeout: 等待关闭按钮出现的最长时间（秒）
    """
    try:
        # 等待关闭按钮出现
        close_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".guide-close-btn.guide-card__close-btn"))
        )
        close_btn.click()
        print("弹窗已关闭")
    except:
        # 超时或没找到就忽略
        print("没有弹窗需要关闭")
    pass

def close_add_to_desktop_ad(driver, timeout=5):
    """
    点击“添加到桌面”弹窗的“下次再说”按钮
    driver: Selenium WebDriver 实例
    timeout: 最长等待秒数
    """
    try:
        # 等待按钮出现并可点击
        next_time_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.van-action-bar-button--first.van-dialog__cancel")
            )
        )
        next_time_btn.click()
        print("已点击“下次再说”按钮，关闭弹窗")
    except:
        # 超时或没找到就忽略
        print("没有“添加到桌面”弹窗出现")

def main():
    if len(sys.argv) < 2 or not sys.argv[1]:
        raise ValueError("Token is empty")
    token = sys.argv[1]
    if not token.endswith("_mhy"):
        raise ValueError("Token is invalid, it should end with '_mhy'")

    driver = initialize_browser()
    try:
        set_cookie(driver, token)
        wait_for_login_status(driver)
        close_save_website_ad(driver)
        close_add_to_desktop_ad(driver)
        ok = wait_for_daily_reward(driver)
        if ok:
            take_screenshot(driver, datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png")
        enter_game(driver)
        ok = choose_channel(driver)
        ok = click_accept(driver)
        click_center_x10(driver)
        take_screenshot(driver, datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png")
        take_domshot(driver, datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".html")
        confuse(driver)
        print("Process completed successfully.")
    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
