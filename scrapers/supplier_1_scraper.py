from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from loguru import logger
import time
import os

from .base_scraper import BaseScraper
from utils.helpers import extract_price, extract_dimensions, clean_text


class Supplier1Scraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(
            supplier_name="Supplier_1",
            base_url="https://supplier1.com",  # Replace with actual URL
            headless=headless
        )
        
        self.login_selectors = {
            'username_field': (By.ID, 'username'),
            'password_field': (By.ID, 'password'),
            'login_button': (By.XPATH, '//button[@type="submit"]')
        }
        
        self.product_selectors = {
            'windows_section': (By.LINK_TEXT, 'Windows'),
            'doors_section': (By.LINK_TEXT, 'Doors'),
            'roofing_section': (By.LINK_TEXT, 'Roofing'),
            
            'width_input': (By.ID, 'width'),
            'height_input': (By.ID, 'height'),
            'material_dropdown': (By.ID, 'material'),
            'color_dropdown': (By.ID, 'color'),
            'calculate_button': (By.ID, 'calculate-price'),
            
            'price_display': (By.CLASS_NAME, 'price-display'),
            'product_details': (By.CLASS_NAME, 'product-details'),
            'specifications': (By.CLASS_NAME, 'specifications')
        }
    
    def login(self) -> bool:
        try:
            username = os.getenv('SUPPLIER_1_USERNAME')
            password = os.getenv('SUPPLIER_1_PASSWORD')
            
            if not username or not password:
                logger.info("No login credentials provided, attempting to proceed without login")
                return True
            
            if not self.browser_manager.safe_send_keys(self.login_selectors['username_field'], username):
                return False
            
            if not self.browser_manager.safe_send_keys(self.login_selectors['password_field'], password):
                return False
            
            if not self.browser_manager.safe_click(self.login_selectors['login_button']):
                return False
            
            time.sleep(3)
            
            if "dashboard" in self.browser_manager.driver.current_url.lower():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - not redirected to dashboard")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def navigate_to_product_section(self, product_type: str) -> bool:
        try:
            section_mapping = {
                'windows': self.product_selectors['windows_section'],
                'doors': self.product_selectors['doors_section'],
                'roofing': self.product_selectors['roofing_section']
            }
            
            selector = section_mapping.get(product_type.lower())
            if not selector:
                logger.error(f"Unknown product type: {product_type}")
                return False
            
            if self.browser_manager.safe_click(selector):
                time.sleep(2)
                logger.info(f"Navigated to {product_type} section")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    def configure_product(self, config: Dict[str, Any]) -> bool:
        try:
            product_type = config.get('product_type')
            if not self.navigate_to_product_section(product_type):
                return False
            
            width = config.get('width')
            if width and not self.browser_manager.safe_send_keys(self.product_selectors['width_input'], str(width)):
                logger.error(f"Failed to set width: {width}")
                return False
            
            height = config.get('height')
            if height and not self.browser_manager.safe_send_keys(self.product_selectors['height_input'], str(height)):
                logger.error(f"Failed to set height: {height}")
                return False
            
            material = config.get('material')
            if material:
                material_element = self.browser_manager.wait_for_element(self.product_selectors['material_dropdown'])
                if material_element:
                    from selenium.webdriver.support.ui import Select
                    select = Select(material_element)
                    try:
                        select.select_by_visible_text(material)
                    except:
                        select.select_by_value(material)
            
            color = config.get('color')
            if color:
                color_element = self.browser_manager.wait_for_element(self.product_selectors['color_dropdown'])
                if color_element:
                    from selenium.webdriver.support.ui import Select
                    select = Select(color_element)
                    try:
                        select.select_by_visible_text(color)
                    except:
                        select.select_by_value(color)
            
            if not self.browser_manager.safe_click(self.product_selectors['calculate_button']):
                logger.error("Failed to click calculate button")
                return False
            
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"Configuration error: {e}")
            return False
    
    def extract_product_data(self) -> Optional[Dict[str, Any]]:
        try:
            product_data = {}
            
            price_text = self.browser_manager.get_element_text(self.product_selectors['price_display'])
            if price_text:
                product_data['price'] = extract_price(price_text)
            
            details_text = self.browser_manager.get_element_text(self.product_selectors['product_details'])
            if details_text:
                product_data['details'] = clean_text(details_text)
                
                dimensions = extract_dimensions(details_text)
                product_data.update(dimensions)
            
            specs_text = self.browser_manager.get_element_text(self.product_selectors['specifications'])
            if specs_text:
                product_data['specifications'] = clean_text(specs_text)
            
            if not product_data.get('price'):
                logger.error("No price found for product")
                return None
            
            return product_data
            
        except Exception as e:
            logger.error(f"Data extraction error: {e}")
            return None
    
    def get_product_configurations(self) -> List[Dict[str, Any]]:
        configurations = []
        
        product_types = ['windows', 'doors']
        dimensions = [
            {'width': 24, 'height': 36},
            {'width': 30, 'height': 48},
            {'width': 36, 'height': 60},
            {'width': 48, 'height': 72}
        ]
        materials = ['vinyl', 'wood', 'aluminum', 'fiberglass']
        colors = ['white', 'brown', 'black', 'bronze']
        
        for product_type in product_types:
            for dimension in dimensions:
                for material in materials:
                    for color in colors:
                        config = {
                            'product_type': product_type,
                            'width': dimension['width'],
                            'height': dimension['height'],
                            'material': material,
                            'color': color
                        }
                        configurations.append(config)
        
        return configurations[:50]  # Limit for testing


if __name__ == "__main__":
    scraper = Supplier1Scraper(headless=False)
    data = scraper.scrape_all_products()
    
    if data:
        scraper.save_data('excel')
        print(f"Scraped {len(data)} products")
        print(scraper.get_summary())