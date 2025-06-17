from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from loguru import logger
import time
import os

from .base_scraper import BaseScraper
from utils.helpers import extract_price, extract_dimensions, clean_text


class Supplier3Scraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(
            supplier_name="Supplier_3",
            base_url="https://supplier3.com",  # Replace with actual URL
            headless=headless
        )
        
        self.login_selectors = {
            'login_link': (By.LINK_TEXT, 'Login'),
            'username_field': (By.ID, 'user-email'),
            'password_field': (By.ID, 'user-password'),
            'login_submit': (By.CSS_SELECTOR, '.login-form input[type="submit"]')
        }
        
        self.product_selectors = {
            'products_menu': (By.CSS_SELECTOR, '.main-nav .products'),
            'windows_link': (By.XPATH, '//a[contains(text(), "Windows")]'),
            'doors_link': (By.XPATH, '//a[contains(text(), "Doors")]'),
            'roofing_link': (By.XPATH, '//a[contains(text(), "Roofing")]'),
            
            'size_calculator': (By.ID, 'size-calculator'),
            'width_field': (By.CSS_SELECTOR, 'input[data-field="width"]'),
            'height_field': (By.CSS_SELECTOR, 'input[data-field="height"]'),
            'material_options': (By.CSS_SELECTOR, '.material-options input[type="radio"]'),
            'color_swatches': (By.CSS_SELECTOR, '.color-options .color-swatch'),
            'upgrade_checkboxes': (By.CSS_SELECTOR, '.upgrades input[type="checkbox"]'),
            
            'calculate_pricing': (By.CSS_SELECTOR, '.calculate-btn'),
            'price_breakdown': (By.CSS_SELECTOR, '.price-breakdown'),
            'total_price': (By.CSS_SELECTOR, '.total-price .amount'),
            'product_specs': (By.CSS_SELECTOR, '.product-specifications'),
            'warranty_info': (By.CSS_SELECTOR, '.warranty-details')
        }
    
    def login(self) -> bool:
        try:
            username = os.getenv('SUPPLIER_3_USERNAME')
            password = os.getenv('SUPPLIER_3_PASSWORD')
            
            if not username or not password:
                logger.info("No login credentials provided for Supplier 3")
                return True
            
            login_link = self.browser_manager.wait_for_element(self.login_selectors['login_link'])
            if login_link:
                login_link.click()
                time.sleep(2)
            
            if not self.browser_manager.safe_send_keys(self.login_selectors['username_field'], username):
                return False
            
            if not self.browser_manager.safe_send_keys(self.login_selectors['password_field'], password):
                return False
            
            if not self.browser_manager.safe_click(self.login_selectors['login_submit']):
                return False
            
            time.sleep(3)
            logger.info("Login completed for Supplier 3")
            return True
                
        except Exception as e:
            logger.error(f"Login error for Supplier 3: {e}")
            return False
    
    def navigate_to_product_section(self, product_type: str) -> bool:
        try:
            products_menu = self.browser_manager.wait_for_element(self.product_selectors['products_menu'])
            if products_menu:
                ActionChains(self.browser_manager.driver).move_to_element(products_menu).perform()
                time.sleep(1)
            
            link_mapping = {
                'windows': self.product_selectors['windows_link'],
                'doors': self.product_selectors['doors_link'],
                'roofing': self.product_selectors['roofing_link']
            }
            
            product_link = link_mapping.get(product_type.lower())
            if product_link:
                if self.browser_manager.safe_click(product_link):
                    time.sleep(3)
                    logger.info(f"Navigated to {product_type} section for Supplier 3")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Navigation error for Supplier 3: {e}")
            return False
    
    def configure_product(self, config: Dict[str, Any]) -> bool:
        try:
            product_type = config.get('product_type')
            if not self.navigate_to_product_section(product_type):
                return False
            
            calculator = self.browser_manager.wait_for_element(self.product_selectors['size_calculator'])
            if not calculator:
                logger.error("Size calculator not found")
                return False
            
            width = config.get('width')
            if width:
                self.browser_manager.safe_send_keys(self.product_selectors['width_field'], str(width))
            
            height = config.get('height')
            if height:
                self.browser_manager.safe_send_keys(self.product_selectors['height_field'], str(height))
            
            material = config.get('material')
            if material:
                material_options = self.browser_manager.driver.find_elements(*self.product_selectors['material_options'])
                for option in material_options:
                    if material.lower() in option.get_attribute('value').lower():
                        option.click()
                        break
            
            color = config.get('color')
            if color:
                color_swatches = self.browser_manager.driver.find_elements(*self.product_selectors['color_swatches'])
                for swatch in color_swatches:
                    if color.lower() in swatch.get_attribute('data-color').lower():
                        swatch.click()
                        break
            
            upgrades = config.get('upgrades', [])
            if upgrades:
                upgrade_checkboxes = self.browser_manager.driver.find_elements(*self.product_selectors['upgrade_checkboxes'])
                for checkbox in upgrade_checkboxes:
                    upgrade_name = checkbox.get_attribute('data-upgrade')
                    if upgrade_name and upgrade_name.lower() in [u.lower() for u in upgrades]:
                        if not checkbox.is_selected():
                            checkbox.click()
            
            if not self.browser_manager.safe_click(self.product_selectors['calculate_pricing']):
                logger.error("Failed to click calculate pricing button")
                return False
            
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"Configuration error for Supplier 3: {e}")
            return False
    
    def extract_product_data(self) -> Optional[Dict[str, Any]]:
        try:
            product_data = {}
            
            total_price_element = self.browser_manager.wait_for_element(self.product_selectors['total_price'], timeout=10)
            if total_price_element:
                price_text = total_price_element.text
                product_data['price'] = extract_price(price_text)
            
            breakdown_element = self.browser_manager.wait_for_element(self.product_selectors['price_breakdown'])
            if breakdown_element:
                breakdown_text = breakdown_element.text
                product_data['price_breakdown'] = clean_text(breakdown_text)
                
                base_price = extract_price(breakdown_text.split('\n')[0]) if '\n' in breakdown_text else None
                if base_price:
                    product_data['base_price'] = base_price
            
            specs_text = self.browser_manager.get_element_text(self.product_selectors['product_specs'])
            if specs_text:
                product_data['specifications'] = clean_text(specs_text)
                
                dimensions = extract_dimensions(specs_text)
                product_data.update(dimensions)
            
            warranty_text = self.browser_manager.get_element_text(self.product_selectors['warranty_info'])
            if warranty_text:
                product_data['warranty'] = clean_text(warranty_text)
            
            installation_elements = self.browser_manager.driver.find_elements(By.XPATH, "//*[contains(text(), 'Installation') or contains(text(), 'Labor')]")
            if installation_elements:
                product_data['installation_info'] = installation_elements[0].text
            
            if not product_data.get('price'):
                logger.error("No price found for Supplier 3 product")
                return None
            
            return product_data
            
        except Exception as e:
            logger.error(f"Data extraction error for Supplier 3: {e}")
            return None
    
    def get_product_configurations(self) -> List[Dict[str, Any]]:
        configurations = []
        
        product_types = ['windows', 'doors']
        dimensions = [
            {'width': 32, 'height': 40},
            {'width': 36, 'height': 46},
            {'width': 40, 'height': 52},
            {'width': 44, 'height': 58}
        ]
        materials = ['vinyl', 'aluminum', 'wood', 'fiberglass']
        colors = ['white', 'beige', 'brown', 'black']
        upgrade_options = [
            [],
            ['low-e-glass'],
            ['security-locks'],
            ['low-e-glass', 'security-locks'],
            ['weatherstripping']
        ]
        
        for product_type in product_types:
            for dimension in dimensions:
                for material in materials:
                    for color in colors:
                        for upgrades in upgrade_options:
                            config = {
                                'product_type': product_type,
                                'width': dimension['width'],
                                'height': dimension['height'],
                                'material': material,
                                'color': color,
                                'upgrades': upgrades
                            }
                            configurations.append(config)
        
        return configurations[:35]  # Limit for testing


if __name__ == "__main__":
    scraper = Supplier3Scraper(headless=False)
    data = scraper.scrape_all_products()
    
    if data:
        scraper.save_data('excel')
        print(f"Scraped {len(data)} products from Supplier 3")
        print(scraper.get_summary())