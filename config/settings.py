import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()


class ScrapingSettings:
    # Browser settings
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'True').lower() == 'true'
    BROWSER_TIMEOUT = int(os.getenv('TIMEOUT_SECONDS', 30))
    
    # Delays and retries
    DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', 2))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    
    # Output settings
    OUTPUT_DIRECTORY = os.getenv('OUTPUT_DIRECTORY', './data/exports')
    EXPORT_FORMAT = os.getenv('EXPORT_FORMAT', 'excel')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIRECTORY = os.getenv('LOG_DIRECTORY', './logs')


class SupplierSettings:
    # Supplier 1 Configuration
    SUPPLIER_1 = {
        'name': 'Supplier_1',
        'base_url': 'https://supplier1.com',  # Replace with actual URL
        'login_required': True,
        'username': os.getenv('SUPPLIER_1_USERNAME'),
        'password': os.getenv('SUPPLIER_1_PASSWORD'),
        'rate_limit': 2.0,  # seconds between requests
        'timeout': 30
    }
    
    # Supplier 2 Configuration
    SUPPLIER_2 = {
        'name': 'Supplier_2',
        'base_url': 'https://supplier2.com',  # Replace with actual URL
        'login_required': True,
        'username': os.getenv('SUPPLIER_2_USERNAME'),
        'password': os.getenv('SUPPLIER_2_PASSWORD'),
        'rate_limit': 3.0,
        'timeout': 45
    }
    
    # Supplier 3 Configuration
    SUPPLIER_3 = {
        'name': 'Supplier_3',
        'base_url': 'https://supplier3.com',  # Replace with actual URL
        'login_required': False,
        'username': os.getenv('SUPPLIER_3_USERNAME'),
        'password': os.getenv('SUPPLIER_3_PASSWORD'),
        'rate_limit': 1.5,
        'timeout': 25
    }


class ProductSettings:
    # Standard product dimensions for testing
    STANDARD_DIMENSIONS = [
        {'width': 24, 'height': 36},
        {'width': 30, 'height': 42},
        {'width': 36, 'height': 48},
        {'width': 42, 'height': 54},
        {'width': 48, 'height': 60},
        {'width': 60, 'height': 72}
    ]
    
    # Common materials
    MATERIALS = [
        'vinyl',
        'wood',
        'aluminum',
        'fiberglass',
        'composite',
        'steel'
    ]
    
    # Common colors
    COLORS = [
        'white',
        'black',
        'brown',
        'bronze',
        'gray',
        'beige',
        'green'
    ]
    
    # Product types
    PRODUCT_TYPES = [
        'windows',
        'doors',
        'roofing'
    ]
    
    # Window specific options
    GLASS_TYPES = [
        'single',
        'double',
        'triple',
        'low-e',
        'tempered'
    ]
    
    # Door specific options
    DOOR_STYLES = [
        'entry',
        'patio',
        'french',
        'sliding',
        'bifold'
    ]
    
    # Roofing specific options
    ROOFING_MATERIALS = [
        'asphalt',
        'metal',
        'tile',
        'slate',
        'wood'
    ]


class DataValidationSettings:
    # Required fields for each product type
    REQUIRED_FIELDS = {
        'windows': ['product_type', 'price', 'width', 'height'],
        'doors': ['product_type', 'price', 'width', 'height'],
        'roofing': ['product_type', 'price', 'material']
    }
    
    # Price validation ranges (in USD)
    PRICE_RANGES = {
        'windows': {'min': 50, 'max': 5000},
        'doors': {'min': 100, 'max': 8000},
        'roofing': {'min': 10, 'max': 1000}  # per sq ft
    }
    
    # Dimension validation ranges (in inches)
    DIMENSION_RANGES = {
        'width': {'min': 12, 'max': 120},
        'height': {'min': 12, 'max': 120}
    }


def get_supplier_config(supplier_name: str) -> Dict[str, Any]:
    """Get configuration for a specific supplier"""
    configs = {
        'supplier1': SupplierSettings.SUPPLIER_1,
        'supplier2': SupplierSettings.SUPPLIER_2,
        'supplier3': SupplierSettings.SUPPLIER_3
    }
    return configs.get(supplier_name.lower(), {})


def get_product_configurations(product_type: str, limit: int = None) -> List[Dict[str, Any]]:
    """Generate product configurations for testing"""
    configurations = []
    
    dimensions = ProductSettings.STANDARD_DIMENSIONS
    materials = ProductSettings.MATERIALS
    colors = ProductSettings.COLORS
    
    if product_type.lower() == 'windows':
        glass_types = ProductSettings.GLASS_TYPES
        for dimension in dimensions:
            for material in materials:
                for color in colors:
                    for glass_type in glass_types:
                        config = {
                            'product_type': 'windows',
                            'width': dimension['width'],
                            'height': dimension['height'],
                            'material': material,
                            'color': color,
                            'glass_type': glass_type
                        }
                        configurations.append(config)
    
    elif product_type.lower() == 'doors':
        door_styles = ProductSettings.DOOR_STYLES
        for dimension in dimensions:
            for material in materials:
                for color in colors:
                    for style in door_styles:
                        config = {
                            'product_type': 'doors',
                            'width': dimension['width'],
                            'height': dimension['height'],
                            'material': material,
                            'color': color,
                            'style': style
                        }
                        configurations.append(config)
    
    elif product_type.lower() == 'roofing':
        roofing_materials = ProductSettings.ROOFING_MATERIALS
        for material in roofing_materials:
            for color in colors:
                config = {
                    'product_type': 'roofing',
                    'material': material,
                    'color': color
                }
                configurations.append(config)
    
    if limit:
        configurations = configurations[:limit]
    
    return configurations