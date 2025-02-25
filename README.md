# Costco Sameday Crawler

A Python script to crawl Costco's sameday delivery produce section and save product information to a CSV file.

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
3. Navigate to the Costco produce section
4. Scrape all product information (name, ID, URL, price)
5. Save the results to `costco_produce_items.csv` in the current directory

### Command-line Options

The script supports several command-line options:

```bash
# Run in visible (non-headless) mode for debugging
python costco_crawler.py --visible

# Change the ZIP code
python costco_crawler.py --zipcode 90210

# Specify a different output file
python costco_crawler.py --output my_costco_items.csv

# Combine options
python costco_crawler.py --visible --zipcode 10001 --output nyc_produce.csv
```

## Debugging

The script includes robust debugging features:

1. **Screenshot capture**: The script automatically takes screenshots at critical points:
   - `initial_page.png`: The Costco Sameday homepage on initial load
   - `before_location.png`: Before entering zip code
   - `after_zip_submission.png`: After zip code submission
   - `location_error.png`: If an error occurs during location setting
   - `produce_page_error.png`: If an error occurs on the product page
   - `no_products_found.png`: If no products can be located

2. **Verbose logging**: The script outputs detailed information about:
   - Selectors being tried
   - Navigation steps
   - Error handling
   - Popup/modal handling

3. **Resilient navigation**: The script attempts multiple methods for:
   - Finding the ZIP code input field
   - Submitting the ZIP code
   - Handling various popups and modals
   - Detecting product listings

4. **Visible mode**: Run with the `--visible` flag to see the browser in action:
   ```bash
   python costco_crawler.py --visible
   ```

## Customization

You can customize the script behavior in several ways:

1. **Command-line options**:
   - `--zipcode` to change the delivery location
   - `--output` to specify a different output filename
   - `--visible` to run with a visible browser window

2. **Code modification**:
   - Edit the `scrape_produce_items` function to extract additional product details
   - Modify selectors if the website structure changes

## Output

The script generates a CSV file with the following columns:
- name: Product name
- id: Product ID
- url: Product URL
- price: Product price

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
   - Check if the website structure has changed
   - Examine the screenshots in the working directory
   - Try running with visible browser: `python costco_crawler.py --visible`

## Deactivating the Virtual Environment

When you're done using the crawler, you can deactivate the virtual environment:

```bash
deactivate
``` 