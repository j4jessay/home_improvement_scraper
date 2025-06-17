#!/usr/bin/env python3

import argparse
import os
from datetime import datetime
from loguru import logger

from scrapers.supplier_1_scraper import Supplier1Scraper
from scrapers.supplier_2_scraper import Supplier2Scraper
from scrapers.supplier_3_scraper import Supplier3Scraper
from utils.data_handler import DataHandler


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"scraper_{timestamp}.log")
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO"
    )


def run_single_scraper(supplier_name: str, headless: bool = True):
    scrapers = {
        'supplier1': Supplier1Scraper,
        'supplier2': Supplier2Scraper,
        'supplier3': Supplier3Scraper
    }
    
    scraper_class = scrapers.get(supplier_name.lower())
    if not scraper_class:
        logger.error(f"Unknown supplier: {supplier_name}")
        return None
    
    logger.info(f"Starting scraper for {supplier_name}")
    scraper = scraper_class(headless=headless)
    
    try:
        data = scraper.scrape_all_products()
        
        if data:
            filepath = scraper.save_data('excel')
            logger.info(f"Data saved to: {filepath}")
            
            summary = scraper.get_summary()
            logger.info(f"Scraping summary: {summary}")
            
            return data
        else:
            logger.warning(f"No data scraped for {supplier_name}")
            return []
            
    except Exception as e:
        logger.error(f"Error running scraper for {supplier_name}: {e}")
        return None


def run_all_scrapers(headless: bool = True):
    logger.info("Starting all scrapers")
    
    all_data = []
    supplier_names = []
    
    scrapers = [
        ('Supplier1', Supplier1Scraper),
        ('Supplier2', Supplier2Scraper),
        ('Supplier3', Supplier3Scraper)
    ]
    
    for supplier_name, scraper_class in scrapers:
        logger.info(f"Running scraper for {supplier_name}")
        
        scraper = scraper_class(headless=headless)
        try:
            data = scraper.scrape_all_products()
            
            if data:
                all_data.append(data)
                supplier_names.append(supplier_name)
                
                scraper.save_data('excel')
                logger.info(f"Completed {supplier_name}: {len(data)} products")
            else:
                logger.warning(f"No data from {supplier_name}")
                
        except Exception as e:
            logger.error(f"Error with {supplier_name}: {e}")
            continue
    
    if all_data:
        data_handler = DataHandler()
        combined_data = data_handler.combine_datasets(all_data, supplier_names)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filepath = data_handler.save_to_excel(combined_data, f"all_suppliers_{timestamp}.xlsx")
        
        summary_report = data_handler.create_summary_report(combined_data)
        pricing_analysis = data_handler.analyze_pricing_patterns(combined_data)
        
        report_data = {
            'summary': summary_report,
            'pricing_analysis': pricing_analysis,
            'scraped_at': datetime.now().isoformat()
        }
        
        report_filepath = data_handler.save_to_json(report_data, f"analysis_report_{timestamp}.json")
        
        logger.info(f"Combined data saved to: {combined_filepath}")
        logger.info(f"Analysis report saved to: {report_filepath}")
        logger.info(f"Total products scraped: {len(combined_data)}")
        
        return combined_data
    
    else:
        logger.error("No data scraped from any supplier")
        return []


def analyze_existing_data(filepath: str):
    try:
        import pandas as pd
        
        if filepath.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            logger.error("Unsupported file format. Use .xlsx or .csv")
            return
        
        data = df.to_dict('records')
        
        data_handler = DataHandler()
        summary = data_handler.create_summary_report(data)
        pricing_analysis = data_handler.analyze_pricing_patterns(data)
        
        print("\n=== DATA ANALYSIS SUMMARY ===")
        print(f"Total Products: {summary['total_products']}")
        print(f"Suppliers: {', '.join(summary['suppliers'])}")
        
        if 'price_analysis' in summary:
            price_info = summary['price_analysis']
            print(f"\nPrice Range: ${price_info['min_price']:.2f} - ${price_info['max_price']:.2f}")
            print(f"Average Price: ${price_info['avg_price']:.2f}")
            print(f"Median Price: ${price_info['median_price']:.2f}")
        
        if 'product_types' in summary:
            print(f"\nProduct Types:")
            for product_type, count in summary['product_types'].items():
                print(f"  {product_type}: {count}")
        
        if pricing_analysis:
            print(f"\n=== PRICING ANALYSIS ===")
            if 'price_per_sqft' in pricing_analysis:
                sqft_info = pricing_analysis['price_per_sqft']
                print(f"Price per Sq Ft: ${sqft_info['min']:.2f} - ${sqft_info['max']:.2f}")
                print(f"Average: ${sqft_info['avg']:.2f}")
        
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")


def main():
    parser = argparse.ArgumentParser(description='Home Improvement Supplier Web Scraper')
    parser.add_argument('--supplier', choices=['supplier1', 'supplier2', 'supplier3', 'all'], 
                       default='all', help='Which supplier to scrape')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode')
    parser.add_argument('--visible', action='store_true',
                       help='Run browser in visible mode (opposite of headless)')
    parser.add_argument('--analyze', type=str,
                       help='Analyze existing data file (provide filepath)')
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.analyze:
        analyze_existing_data(args.analyze)
        return
    
    headless = args.headless and not args.visible
    
    if args.supplier == 'all':
        run_all_scrapers(headless=headless)
    else:
        run_single_scraper(args.supplier, headless=headless)


if __name__ == "__main__":
    main()