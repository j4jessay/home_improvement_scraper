import re
import time
import random
from typing import List, Dict, Any, Optional
from loguru import logger
from retrying import retry


def extract_price(text: str) -> Optional[float]:
    if not text:
        return None
    
    price_patterns = [
        r'\$?(\d+,?\d*\.?\d+)',
        r'(\d+,?\d*\.?\d+)\s*\$',
        r'Price:\s*\$?(\d+,?\d*\.?\d+)',
        r'Cost:\s*\$?(\d+,?\d*\.?\d+)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text.replace(',', ''))
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                continue
    
    return None


def extract_dimensions(text: str) -> Dict[str, Optional[float]]:
    dimensions = {'width': None, 'height': None}
    
    patterns = [
        r'(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)',
        r'Width:\s*(\d+\.?\d*).+Height:\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*W\s*[x×]\s*(\d+\.?\d*)\s*H',
        r'(\d+\.?\d*)"?\s*[x×]\s*(\d+\.?\d*)"?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                dimensions['width'] = float(match.group(1))
                dimensions['height'] = float(match.group(2))
                break
            except ValueError:
                continue
    
    return dimensions


def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    text = re.sub(r'[^\w\s\-\.\$\(\)\/]', '', text)
    
    return text


def random_delay(min_seconds: float = 1.0, max_seconds: float = 3.0):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def retry_on_failure(max_attempts: int = 3, delay_seconds: int = 5):
    return retry(
        stop_max_attempt_number=max_attempts,
        wait_fixed=delay_seconds * 1000,
        retry_on_exception=lambda x: isinstance(x, Exception)
    )


def validate_product_data(product: Dict[str, Any]) -> bool:
    required_fields = ['product_type', 'price']
    
    for field in required_fields:
        if field not in product or product[field] is None:
            logger.warning(f"Product missing required field: {field}")
            return False
    
    try:
        float(product['price'])
    except (ValueError, TypeError):
        logger.warning(f"Invalid price format: {product.get('price')}")
        return False
    
    return True


def normalize_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {}
    
    field_mapping = {
        'product_type': ['type', 'product_type', 'category'],
        'price': ['price', 'cost', 'total_price', 'amount'],
        'width': ['width', 'w', 'dimension_width'],
        'height': ['height', 'h', 'dimension_height'],
        'material': ['material', 'frame_material', 'construction'],
        'color': ['color', 'finish', 'paint_color'],
        'brand': ['brand', 'manufacturer', 'make'],
        'model': ['model', 'model_number', 'part_number'],
        'features': ['features', 'options', 'upgrades'],
        'delivery_time': ['delivery', 'lead_time', 'shipping_time']
    }
    
    for standard_field, possible_fields in field_mapping.items():
        for field in possible_fields:
            if field in product and product[field] is not None:
                normalized[standard_field] = product[field]
                break
    
    if 'price' in normalized:
        if isinstance(normalized['price'], str):
            normalized['price'] = extract_price(normalized['price'])
    
    return normalized


def create_product_variations(base_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    variations = []
    
    dimension_options = base_config.get('dimensions', [])
    material_options = base_config.get('materials', [])
    color_options = base_config.get('colors', [])
    
    if not dimension_options:
        dimension_options = [None]
    if not material_options:
        material_options = [None]
    if not color_options:
        color_options = [None]
    
    for dimension in dimension_options:
        for material in material_options:
            for color in color_options:
                variation = base_config.copy()
                
                if dimension:
                    variation.update(dimension)
                if material:
                    variation['material'] = material
                if color:
                    variation['color'] = color
                
                variations.append(variation)
    
    return variations


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def log_scraping_progress(current: int, total: int, item_name: str = "items"):
    percentage = (current / total) * 100
    logger.info(f"Progress: {current}/{total} {item_name} ({percentage:.1f}%)")