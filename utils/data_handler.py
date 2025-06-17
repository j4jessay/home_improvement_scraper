import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger


class DataHandler:
    def __init__(self, output_dir: str = "./data/exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_to_excel(self, data: List[Dict[str, Any]], filename: str = None, sheet_name: str = "Products") -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.xlsx"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_excel(filepath, sheet_name=sheet_name, index=False)
            logger.info(f"Data saved to Excel: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            raise
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            logger.info(f"Data saved to CSV: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save CSV file: {e}")
            raise
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Data saved to JSON: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save JSON file: {e}")
            raise
    
    def combine_datasets(self, datasets: List[List[Dict[str, Any]]], supplier_names: List[str]) -> List[Dict[str, Any]]:
        combined_data = []
        
        for i, dataset in enumerate(datasets):
            supplier_name = supplier_names[i] if i < len(supplier_names) else f"Supplier_{i+1}"
            
            for item in dataset:
                item['supplier'] = supplier_name
                item['scraped_at'] = datetime.now().isoformat()
                combined_data.append(item)
        
        return combined_data
    
    def create_summary_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        df = pd.DataFrame(data)
        
        summary = {
            'total_products': len(df),
            'suppliers': df['supplier'].unique().tolist() if 'supplier' in df.columns else [],
            'date_range': {
                'start': df['scraped_at'].min() if 'scraped_at' in df.columns else None,
                'end': df['scraped_at'].max() if 'scraped_at' in df.columns else None
            }
        }
        
        if 'price' in df.columns:
            summary['price_analysis'] = {
                'min_price': float(df['price'].min()),
                'max_price': float(df['price'].max()),
                'avg_price': float(df['price'].mean()),
                'median_price': float(df['price'].median())
            }
        
        if 'product_type' in df.columns:
            summary['product_types'] = df['product_type'].value_counts().to_dict()
        
        return summary
    
    def analyze_pricing_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        df = pd.DataFrame(data)
        
        patterns = {}
        
        if 'width' in df.columns and 'height' in df.columns and 'price' in df.columns:
            df['area'] = pd.to_numeric(df['width'], errors='coerce') * pd.to_numeric(df['height'], errors='coerce')
            df['price_per_sqft'] = pd.to_numeric(df['price'], errors='coerce') / df['area']
            
            patterns['price_per_sqft'] = {
                'min': float(df['price_per_sqft'].min()),
                'max': float(df['price_per_sqft'].max()),
                'avg': float(df['price_per_sqft'].mean())
            }
        
        if 'material' in df.columns and 'price' in df.columns:
            material_pricing = df.groupby('material')['price'].agg(['mean', 'min', 'max']).to_dict()
            patterns['material_pricing'] = material_pricing
        
        if 'color' in df.columns and 'price' in df.columns:
            color_pricing = df.groupby('color')['price'].agg(['mean', 'min', 'max']).to_dict()
            patterns['color_pricing'] = color_pricing
        
        return patterns