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
        WebDriverWait(driver, 10).until(
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
        WebDriverWait(driver, 10).until(lambda d: "每日登陆奖励" in d.page_source)
    except Exception as e:
        raise RuntimeError("Daily login reward not found") from e


def take_screenshot(driver, filename):
    print("Daily login reward found, taking screenshot...")
    for element in driver.find_elements(By.CLASS_NAME, "van-overlay"):
        driver.execute_script("arguments[0].remove();", element)
    driver.save_screenshot(filename)


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
        wait_for_daily_reward(driver)
        take_screenshot(driver, datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png")
        print("Process completed successfully.")
    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
