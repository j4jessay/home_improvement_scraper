from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from loguru import logger
import time
import os

from .base_scraper import BaseScraper
from utils.helpers import extract_price, extract_dimensions, clean_text


class Supplier2Scraper(BaseScraper):
    def __init__(self, headless: bool = True):
        super().__init__(
            supplier_name="Supplier_2",
            base_url="https://supplier2.com",  # Replace with actual URL
            headless=headless
        )
        
        self.login_selectors = {
            'username_field': (By.NAME, 'email'),
            'password_field': (By.NAME, 'password'),
            'login_button': (By.CSS_SELECTOR, 'button[type="submit"]')
        }
        
        self.product_selectors = {
            'product_configurator': (By.ID, 'product-configurator'),
            'category_select': (By.ID, 'category'),
            'subcategory_select': (By.ID, 'subcategory'),
            
            'dimension_width': (By.NAME, 'dimension_width'),
            'dimension_height': (By.NAME, 'dimension_height'),
            'frame_material': (By.NAME, 'frame_material'),
            'finish_color': (By.NAME, 'finish_color'),
            'glass_type': (By.NAME, 'glass_type'),
            
            'quote_button': (By.ID, 'get-quote'),
            'price_container': (By.CLASS_NAME, 'quote-price'),
            'product_summary': (By.CLASS_NAME, 'product-summary'),
            'feature_list': (By.CLASS_NAME, 'feature-list')
        }
    
    def login(self) -> bool:
        try:
            username = os.getenv('SUPPLIER_2_USERNAME')
            password = os.getenv('SUPPLIER_2_PASSWORD')
            
            if not username or not password:
                logger.info("No login credentials provided for Supplier 2")
                return True
            
            if not self.browser_manager.safe_send_keys(self.login_selectors['username_field'], username):
                return False
            
            if not self.browser_manager.safe_send_keys(self.login_selectors['password_field'], password):
                return False
            
            if not self.browser_manager.safe_click(self.login_selectors['login_button']):
                return False
            
            time.sleep(3)
            logger.info("Login completed for Supplier 2")
            return True
                
        except Exception as e:
            logger.error(f"Login error for Supplier 2: {e}")
            return False
    
    def navigate_to_product_section(self, product_type: str) -> bool:
        try:
            configurator = self.browser_manager.wait_for_element(self.product_selectors['product_configurator'])
            if not configurator:
                logger.error("Product configurator not found")
                return False
            
            category_element = self.browser_manager.wait_for_element(self.product_selectors['category_select'])
            if category_element:
                from selenium.webdriver.support.ui import Select
                select = Select(category_element)
                
                category_mapping = {
                    'windows': 'Windows & Glazing',
                    'doors': 'Doors & Entries',
                    'roofing': 'Roofing Systems'
                }
                
                category = category_mapping.get(product_type.lower(), product_type)
                select.select_by_visible_text(category)
                time.sleep(2)
            
            logger.info(f"Navigated to {product_type} configurator")
            return True
            
        except Exception as e:
            logger.error(f"Navigation error for Supplier 2: {e}")
            return False
    
    def configure_product(self, config: Dict[str, Any]) -> bool:
        try:
            product_type = config.get('product_type')
            if not self.navigate_to_product_section(product_type):
                return False
            
            width = config.get('width')
            if width:
                self.browser_manager.safe_send_keys(self.product_selectors['dimension_width'], str(width))
            
            height = config.get('height')
            if height:
                self.browser_manager.safe_send_keys(self.product_selectors['dimension_height'], str(height))
            
            material = config.get('material')
            if material:
                material_element = self.browser_manager.wait_for_element(self.product_selectors['frame_material'])
                if material_element:
                    from selenium.webdriver.support.ui import Select
                    select = Select(material_element)
                    try:
                        select.select_by_visible_text(material.title())
                    except:
                        try:
                            select.select_by_value(material.lower())
                        except:
                            logger.warning(f"Could not select material: {material}")
            
            color = config.get('color')
            if color:
                color_element = self.browser_manager.wait_for_element(self.product_selectors['finish_color'])
                if color_element:
                    from selenium.webdriver.support.ui import Select
                    select = Select(color_element)
                    try:
                        select.select_by_visible_text(color.title())
                    except:
                        try:
                            select.select_by_value(color.lower())
                        except:
                            logger.warning(f"Could not select color: {color}")
            
            glass_type = config.get('glass_type', 'double')
            glass_element = self.browser_manager.wait_for_element(self.product_selectors['glass_type'])
            if glass_element:
                from selenium.webdriver.support.ui import Select
                select = Select(glass_element)
                try:
                    select.select_by_visible_text(glass_type.title())
                except:
                    pass
            
            if not self.browser_manager.safe_click(self.product_selectors['quote_button']):
                logger.error("Failed to click quote button")
                return False
            
            time.sleep(4)
            return True
            
        except Exception as e:
            logger.error(f"Configuration error for Supplier 2: {e}")
            return False
    
    def extract_product_data(self) -> Optional[Dict[str, Any]]:
        try:
            product_data = {}
            
            price_element = self.browser_manager.wait_for_element(self.product_selectors['price_container'], timeout=10)
            if price_element:
                price_text = price_element.text
                product_data['price'] = extract_price(price_text)
            
            summary_text = self.browser_manager.get_element_text(self.product_selectors['product_summary'])
            if summary_text:
                product_data['summary'] = clean_text(summary_text)
                
                dimensions = extract_dimensions(summary_text)
                product_data.update(dimensions)
            
            features_text = self.browser_manager.get_element_text(self.product_selectors['feature_list'])
            if features_text:
                product_data['features'] = clean_text(features_text)
            
            lead_time_element = self.browser_manager.driver.find_elements(By.XPATH, "//*[contains(text(), 'Lead Time') or contains(text(), 'Delivery')]")
            if lead_time_element:
                product_data['delivery_info'] = lead_time_element[0].text
            
            if not product_data.get('price'):
                logger.error("No price found for Supplier 2 product")
                return None
            
            return product_data
            
        except Exception as e:
            logger.error(f"Data extraction error for Supplier 2: {e}")
            return None
    
    def get_product_configurations(self) -> List[Dict[str, Any]]:
        configurations = []
        
        product_types = ['windows', 'doors']
        dimensions = [
            {'width': 30, 'height': 42},
            {'width': 36, 'height': 48},
            {'width': 42, 'height': 54},
            {'width': 48, 'height': 60}
        ]
        materials = ['vinyl', 'aluminum', 'wood', 'composite']
        colors = ['white', 'bronze', 'black', 'gray']
        glass_types = ['single', 'double', 'triple']
        
        for product_type in product_types:
            for dimension in dimensions:
                for material in materials:
                    for color in colors:
                        for glass_type in glass_types:
                            config = {
                                'product_type': product_type,
                                'width': dimension['width'],
                                'height': dimension['height'],
                                'material': material,
                                'color': color,
                                'glass_type': glass_type
                            }
                            configurations.append(config)
        
        return configurations[:40]  # Limit for testing


if __name__ == "__main__":
    scraper = Supplier2Scraper(headless=False)
    data = scraper.scrape_all_products()
    
    if data:
        scraper.save_data('excel')
        print(f"Scraped {len(data)} products from Supplier 2")
        print(scraper.get_summary())