from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from loguru import logger
from dotenv import load_dotenv

from utils.browser_manager import BrowserManager
from utils.data_handler import DataHandler
from utils.helpers import random_delay, retry_on_failure, validate_product_data, normalize_product_data

load_dotenv()


class BaseScraper(ABC):
    def __init__(self, supplier_name: str, base_url: str, headless: bool = True):
        self.supplier_name = supplier_name
        self.base_url = base_url
        self.headless = headless
        
        self.browser_manager = BrowserManager(headless=headless)
        self.data_handler = DataHandler()
        
        self.scraped_data = []
        self.failed_items = []
        
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.delay_between_requests = float(os.getenv('DELAY_BETWEEN_REQUESTS', 2))
    
    def setup(self):
        logger.info(f"Setting up scraper for {self.supplier_name}")
        self.browser_manager.start_browser()
        self.browser_manager.navigate_to_url(self.base_url)
    
    def cleanup(self):
        logger.info(f"Cleaning up scraper for {self.supplier_name}")
        self.browser_manager.close_browser()
    
    @abstractmethod
    def login(self) -> bool:
        pass
    
    @abstractmethod
    def navigate_to_product_section(self, product_type: str) -> bool:
        pass
    
    @abstractmethod
    def configure_product(self, config: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    def extract_product_data(self) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_product_configurations(self) -> List[Dict[str, Any]]:
        pass
    
    @retry_on_failure(max_attempts=3)
    def scrape_single_product(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Scraping product: {config}")
            
            if not self.configure_product(config):
                logger.error(f"Failed to configure product: {config}")
                return None
            
            random_delay(self.delay_between_requests, self.delay_between_requests + 1)
            
            product_data = self.extract_product_data()
            
            if not product_data:
                logger.error(f"Failed to extract data for: {config}")
                return None
            
            product_data.update(config)
            product_data['supplier'] = self.supplier_name
            
            normalized_data = normalize_product_data(product_data)
            
            if validate_product_data(normalized_data):
                return normalized_data
            else:
                logger.error(f"Invalid product data: {normalized_data}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping product {config}: {e}")
            self.browser_manager.take_screenshot(f"error_{self.supplier_name}_{len(self.failed_items)}.png")
            return None
    
    def scrape_all_products(self) -> List[Dict[str, Any]]:
        logger.info(f"Starting scraping for {self.supplier_name}")
        
        try:
            self.setup()
            
            if not self.login():
                logger.error("Failed to login")
                return []
            
            configurations = self.get_product_configurations()
            logger.info(f"Found {len(configurations)} product configurations to scrape")
            
            for i, config in enumerate(configurations):
                logger.info(f"Processing configuration {i+1}/{len(configurations)}")
                
                product_data = self.scrape_single_product(config)
                
                if product_data:
                    self.scraped_data.append(product_data)
                    logger.info(f"Successfully scraped: {product_data.get('product_type', 'Unknown')}")
                else:
                    self.failed_items.append(config)
                    logger.warning(f"Failed to scrape: {config}")
                
                random_delay(self.delay_between_requests, self.delay_between_requests + 2)
            
            logger.info(f"Scraping completed. Success: {len(self.scraped_data)}, Failed: {len(self.failed_items)}")
            
        except Exception as e:
            logger.error(f"Fatal error during scraping: {e}")
            self.browser_manager.take_screenshot(f"fatal_error_{self.supplier_name}.png")
        
        finally:
            self.cleanup()
        
        return self.scraped_data
    
    def save_data(self, format_type: str = 'excel') -> str:
        if not self.scraped_data:
            logger.warning("No data to save")
            return None
        
        filename = f"{self.supplier_name}_products"
        
        if format_type.lower() == 'excel':
            return self.data_handler.save_to_excel(self.scraped_data, f"{filename}.xlsx")
        elif format_type.lower() == 'csv':
            return self.data_handler.save_to_csv(self.scraped_data, f"{filename}.csv")
        elif format_type.lower() == 'json':
            return self.data_handler.save_to_json(self.scraped_data, f"{filename}.json")
        else:
            logger.error(f"Unsupported format: {format_type}")
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            'supplier': self.supplier_name,
            'total_scraped': len(self.scraped_data),
            'total_failed': len(self.failed_items),
            'success_rate': len(self.scraped_data) / (len(self.scraped_data) + len(self.failed_items)) * 100 if (len(self.scraped_data) + len(self.failed_items)) > 0 else 0,
            'failed_configurations': self.failed_items
        }