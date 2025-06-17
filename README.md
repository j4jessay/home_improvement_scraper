# Home Improvement Supplier Web Scraper

A comprehensive web scraping solution for extracting product pricing and configuration data from home improvement supplier websites specializing in windows, doors, and roofing systems.

## Features

- **Multi-Supplier Support**: Scrape data from three different supplier websites
- **Product Configuration**: Handle complex forms with dimensions, materials, colors, and upgrades
- **Price Extraction**: Extract structured pricing data and analyze pricing patterns
- **Data Export**: Export data to Excel, CSV, or JSON formats
- **Analysis Tools**: Built-in data analysis and reporting capabilities
- **Robust Error Handling**: Retry mechanisms and comprehensive logging
- **Stealth Browsing**: Anti-detection measures with rotating user agents

## Project Structure

```
home_improvement_scraper/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration settings
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py      # Base scraper class
│   ├── supplier_1_scraper.py
│   ├── supplier_2_scraper.py
│   └── supplier_3_scraper.py
├── utils/
│   ├── __init__.py
│   ├── browser_manager.py   # Browser automation utilities
│   ├── data_handler.py      # Data processing and export
│   └── helpers.py           # Helper functions
├── data/
│   └── exports/             # Output files
├── logs/                    # Log files
├── main.py                  # Main execution script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md
```

## Installation

1. **Clone or download the project**:
   ```bash
   cd home_improvement_scraper
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers** (if using Playwright):
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your supplier credentials
   ```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Supplier Website Credentials (if needed)
SUPPLIER_1_USERNAME=your_username
SUPPLIER_1_PASSWORD=your_password
SUPPLIER_2_USERNAME=your_username
SUPPLIER_2_PASSWORD=your_password
SUPPLIER_3_USERNAME=your_username
SUPPLIER_3_PASSWORD=your_password

# Scraping Configuration
DELAY_BETWEEN_REQUESTS=2
MAX_RETRIES=3
TIMEOUT_SECONDS=30
HEADLESS_MODE=True

# Data Export Settings
EXPORT_FORMAT=excel
OUTPUT_DIRECTORY=./data/exports
```

### Supplier Configuration

Update the supplier URLs and selectors in each scraper class:

1. `scrapers/supplier_1_scraper.py` - Update `base_url` and selectors
2. `scrapers/supplier_2_scraper.py` - Update `base_url` and selectors  
3. `scrapers/supplier_3_scraper.py` - Update `base_url` and selectors

## Usage

### Command Line Interface

```bash
# Scrape all suppliers
python main.py --supplier all

# Scrape specific supplier
python main.py --supplier supplier1

# Run in visible browser mode (for debugging)
python main.py --supplier supplier1 --visible

# Analyze existing data
python main.py --analyze ./data/exports/scraped_data.xlsx
```

### Programmatic Usage

```python
from scrapers.supplier_1_scraper import Supplier1Scraper

# Initialize scraper
scraper = Supplier1Scraper(headless=True)

# Scrape all products
data = scraper.scrape_all_products()

# Save data
scraper.save_data('excel')

# Get summary
summary = scraper.get_summary()
print(f"Scraped {summary['total_scraped']} products")
```

## Customization

### Adding New Suppliers

1. **Create new scraper class**:
   ```python
   from scrapers.base_scraper import BaseScraper
   
   class NewSupplierScraper(BaseScraper):
       def __init__(self):
           super().__init__("NewSupplier", "https://newsupplier.com")
       
       def login(self):
           # Implement login logic
           pass
       
       def configure_product(self, config):
           # Implement product configuration
           pass
       
       def extract_product_data(self):
           # Implement data extraction
           pass
   ```

2. **Update main.py** to include the new scraper

### Modifying Product Configurations

Edit `config/settings.py` to modify:
- Product dimensions
- Material options
- Color choices
- Product types

### Custom Data Processing

Extend `utils/data_handler.py` for custom analysis:

```python
def custom_analysis(self, data):
    df = pd.DataFrame(data)
    # Add your custom analysis logic
    return analysis_results
```

## Data Output

### Excel Export
- **Sheet 1**: Raw product data
- **Columns**: product_type, price, width, height, material, color, supplier, scraped_at

### CSV Export
- Flat file with all product information
- Suitable for database imports

### JSON Export
- Structured data with nested information
- Includes metadata and analysis results

### Analysis Report
- Summary statistics
- Price analysis by material/color
- Pricing patterns and trends

## Error Handling

- **Retry Logic**: Automatically retries failed requests
- **Screenshot Capture**: Takes screenshots on errors
- **Comprehensive Logging**: Detailed logs for debugging
- **Graceful Degradation**: Continues operation if some products fail

## Anti-Detection Features

- **Rotating User Agents**: Mimics different browsers
- **Random Delays**: Varies request timing
- **Stealth Mode**: Disables automation detection
- **Proxy Support**: Can be extended for proxy rotation

## Monitoring and Logging

- **Structured Logging**: Uses loguru for comprehensive logging
- **Progress Tracking**: Real-time progress updates
- **Error Reporting**: Detailed error logs with context
- **Performance Metrics**: Scraping speed and success rates

## Best Practices

1. **Respect Rate Limits**: Configure appropriate delays
2. **Monitor Website Changes**: Regularly update selectors
3. **Handle Dynamic Content**: Use proper waits for JavaScript
4. **Data Validation**: Verify extracted data quality
5. **Legal Compliance**: Ensure scraping complies with terms of service

## Troubleshooting

### Common Issues

1. **Login Failures**:
   - Verify credentials in `.env`
   - Check if CAPTCHA is required
   - Update login selectors

2. **Element Not Found**:
   - Website structure may have changed
   - Update CSS selectors
   - Increase timeout values

3. **Price Extraction Issues**:
   - Check price format patterns
   - Update regex in `helpers.py`
   - Verify currency symbols

4. **Performance Issues**:
   - Reduce concurrent requests
   - Increase delays between requests
   - Use headless mode

### Debug Mode

Run with visible browser for debugging:
```bash
python main.py --supplier supplier1 --visible
```

## License

This project is provided as-is for web scraping purposes. Ensure compliance with each website's terms of service and robots.txt file.

## Support

For issues and questions:
1. Check the logs in `./logs/` directory
2. Review the configuration settings
3. Verify website selectors are current
4. Test with visible browser mode

## Future Enhancements

- [ ] Proxy rotation support
- [ ] Database integration
- [ ] Real-time price monitoring
- [ ] Email notifications
- [ ] API endpoints
- [ ] Docker containerization
- [ ] Cloud deployment options