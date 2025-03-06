# Costco Sameday Crawler

A Python script to crawl Costco's sameday delivery sections and save product information to a CSV file. Supports multiple departments and categories.

## Requirements

- Python 3.7 or higher
- Chrome browser installed

## Installation

1. Clone this repository or download the files.
2. Create and activate a virtual environment:

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Special Instructions for macOS Apple Silicon (M1/M2/M3) Users

If you're using a Mac with Apple Silicon (ARM architecture), you may need to install ChromeDriver through Homebrew for better compatibility:

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ChromeDriver
brew install chromedriver

# Give it proper permissions
xattr -d com.apple.quarantine $(which chromedriver)
```

The script will attempt to use the Homebrew-installed ChromeDriver when running on Apple Silicon Macs.

## Usage

Run the script with:

```bash
python costco_crawler.py
```

This will:
1. Launch a headless Chrome browser
2. Set the delivery location to zip code 94107 (San Francisco)
3. Navigate to the specified Costco department (defaults to produce)
4. Scrape all product information (name, ID, URL, image URL, price)
5. Save the results to a CSV file named `costco_[category]_items_[zipcode]_[date].csv`

### Available Categories

The script supports all major Costco Sameday departments:

- `produce` - Fresh Produce
- `bakery` - Bakery & Desserts
- `meat` - Meat & Seafood
- `deli` - Deli
- `dairy` - Dairy & Eggs
- `beverages` - Beverages
- `pantry` - Pantry & Dry Goods
- `snacks` - Snacks, Candy & Nuts
- `frozen` - Frozen Foods
- `household` - Home Essentials
- `health` - Health & Personal Care
- `baby` - Baby Products
- `pet` - Pet Supplies
- `alcohol` - Beer, Wine & Spirits
- `auto` - Auto Accessories
- `cleaning` - Cleaning & Laundry
- `clothing` - Clothing Basics
- `electronics` - Electronics & Computers
- `garden` - Home Improvement & Garden
- `jewelry` - Jewelry & Watches
- `office` - Office Products
- `paper` - Paper Products & Food Storage
- `sports` - Sporting Goods
- `toys` - Toys & Seasonal

Special Collections:
- `whats-new` - What's New
- `weekly-savings` - Weekly Savings
- `trending` - Trending Items
- `kirkland` - Kirkland Signature Products

### Command-line Options

The script supports several command-line options:

```bash
# Specify a category to crawl
python costco_crawler.py --category bakery

# Run in visible (non-headless) mode for debugging
python costco_crawler.py --visible

# Change the ZIP code
python costco_crawler.py --zipcode 90210

# Specify a different output file
python costco_crawler.py --output my_costco_items.csv

# Limit the number of items (useful for testing)
python costco_crawler.py --max 10

# Combine options
python costco_crawler.py --category electronics --visible --zipcode 10001 --output nyc_electronics.csv
```

## Debugging

The script includes robust debugging features:

1. **Screenshot capture**: The script automatically takes screenshots at critical points:
   - `before_location.png`: Before entering zip code
   - `[category]_page_loaded.png`: After loading the category page
   - `[category]_page_source.html`: HTML source for debugging
   - `after_scrolling.png`: After scrolling to load all items
   - `no_products_found.png`: If no products can be located

2. **Verbose logging**: The script outputs detailed information about:
   - Category and URL being accessed
   - Selectors being tried
   - Navigation steps
   - Error handling
   - Popup/modal handling
   - Product processing progress

3. **Improved Scrolling**: The script uses an enhanced scrolling mechanism:
   - Progressive scrolling (75% of viewport height at a time)
   - Increased wait time between scrolls (5 seconds)
   - More scroll attempts (15 maximum)
   - Better detection of page bottom
   - Improved handling of lazy-loaded content

4. **Resilient navigation**: The script attempts multiple methods for:
   - Finding the ZIP code input field
   - Submitting the ZIP code
   - Handling various popups and modals
   - Detecting product listings
   - Extracting product information

5. **Visible mode**: Run with the `--visible` flag to see the browser in action:
   ```bash
   python costco_crawler.py --visible
   ```

## Output

The script generates a CSV file with the following columns:
- name: Product name
- id: Product ID (Costco item number when available)
- url: Product URL
- image_url: High-resolution product image URL
- price: Product price

The output filename follows the pattern: `costco_[category]_items_[zipcode]_[date].csv`

## Troubleshooting

If you encounter issues:

1. **ChromeDriver errors**:
   - Make sure Chrome browser is installed
   - For macOS users, try installing ChromeDriver via Homebrew as described above
   - Run ChromeDriver manually to check for errors: `chromedriver --version`
   - Check that ChromeDriver version matches your Chrome browser version

2. **"Failed to set location" error**:
   - Check the screenshots in the working directory for clues
   - Verify the ZIP code is valid for Costco Sameday delivery
   - Try running with visible mode for debugging: `python costco_crawler.py --visible`

3. **"No items found" error**:
   - Verify the category exists and is spelled correctly
   - Check if the website structure has changed
   - Examine the category page source HTML saved in `[category]_page_source.html`
   - Look at the screenshots in the working directory
   - Try running with visible browser: `python costco_crawler.py --visible --category [category]`

4. **Scrolling issues**:
   - If items are being missed, try running in visible mode to observe the scrolling
   - Check network connectivity as slow connections may need more time to load
   - Consider increasing the wait time between scrolls in the code
   - Verify that JavaScript is enabled in the browser

5. **Age verification for alcohol**:
   - Note that the `alcohol` category may require additional age verification
   - The script currently does not handle age verification popups
   - Consider using other categories if age verification is required

## Deactivating the Virtual Environment

When you're done using the crawler, you can deactivate the virtual environment:

```bash
deactivate
``` 