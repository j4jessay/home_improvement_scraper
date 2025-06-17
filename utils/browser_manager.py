import os
import time
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
from loguru import logger
import undetected_chromedriver as uc


class BrowserManager:
    def __init__(self, headless: bool = True, timeout: int = 30):
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.wait = None
        
    def setup_chrome_options(self) -> Options:
        options = Options()
        ua = UserAgent()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={ua.random}')
        options.add_argument('--window-size=1920,1080')
        
        return options
    
    def start_browser(self) -> webdriver.Chrome:
        try:
            options = self.setup_chrome_options()
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, self.timeout)
            logger.info("Browser started successfully")
            return self.driver
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def navigate_to_url(self, url: str) -> bool:
        try:
            self.driver.get(url)
            time.sleep(2)
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def wait_for_element(self, locator: tuple, timeout: Optional[int] = None) -> Optional[Any]:
        try:
            timeout = timeout or self.timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {locator}")
            return None
    
    def wait_for_clickable(self, locator: tuple, timeout: Optional[int] = None) -> Optional[Any]:
        try:
            timeout = timeout or self.timeout
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            logger.warning(f"Element not clickable: {locator}")
            return None
    
    def safe_click(self, locator: tuple, timeout: Optional[int] = None) -> bool:
        try:
            element = self.wait_for_clickable(locator, timeout)
            if element:
                element.click()
                time.sleep(1)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click element {locator}: {e}")
            return False
    
    def safe_send_keys(self, locator: tuple, text: str, clear_first: bool = True) -> bool:
        try:
            element = self.wait_for_element(locator)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send keys to element {locator}: {e}")
            return False
    
    def get_element_text(self, locator: tuple) -> Optional[str]:
        try:
            element = self.wait_for_element(locator)
            if element:
                return element.text.strip()
            return None
        except Exception as e:
            logger.error(f"Failed to get text from element {locator}: {e}")
            return None
    
    def get_element_attribute(self, locator: tuple, attribute: str) -> Optional[str]:
        try:
            element = self.wait_for_element(locator)
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            logger.error(f"Failed to get attribute {attribute} from element {locator}: {e}")
            return None
    
    def take_screenshot(self, filename: str = None) -> str:
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        filepath = os.path.join("logs", filename)
        os.makedirs("logs", exist_ok=True)
        
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def close_browser(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")