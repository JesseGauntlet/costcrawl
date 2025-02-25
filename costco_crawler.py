import os
import csv
import time
import platform
import subprocess
import argparse
import datetime  # Add this import for date handling
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

def setup_driver(headless=True):
    """Set up and return a configured Chrome webdriver."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if headless:
        chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Special handling for Mac
    is_mac = platform.system() == 'Darwin'
    is_arm = 'arm' in platform.machine().lower()
    
    if is_mac and is_arm:
        print("Detected macOS on ARM architecture (Apple Silicon)")
        try:
            # Try to use homebrew installed chromedriver if available
            # Check if chromedriver is installed via homebrew
            try:
                subprocess.run(["brew", "--version"], check=True, capture_output=True)
                print("Homebrew is installed, checking for chromedriver...")
                result = subprocess.run(["brew", "list", "chromedriver"], check=False, capture_output=True)
                
                if result.returncode == 0:
                    print("Using homebrew installed chromedriver")
                    chrome_path = subprocess.run(["which", "chromedriver"], check=True, 
                                           capture_output=True, text=True).stdout.strip()
                    service = Service(executable_path=chrome_path)
                else:
                    print("Chromedriver not installed via homebrew. Installing it now...")
                    subprocess.run(["brew", "install", "chromedriver"], check=True)
                    chrome_path = subprocess.run(["which", "chromedriver"], check=True, 
                                           capture_output=True, text=True).stdout.strip()
                    service = Service(executable_path=chrome_path)
            except (subprocess.SubprocessError, FileNotFoundError):
                print("Homebrew not available, falling back to webdriver_manager...")
                service = Service(ChromeDriverManager().install())
        except Exception as e:
            print(f"Error setting up chromedriver: {e}")
            print("Falling back to default webdriver_manager...")
            service = Service(ChromeDriverManager().install())
    else:
        # For non-Mac or Intel Mac
        service = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("Try installing Chrome browser if not already installed")
        raise

def set_location(driver, zipcode="94107"):
    """Set the delivery location using the provided zipcode."""
    driver.get("https://sameday.costco.com")
    print("Navigated to Costco Sameday website")
    
    try:
        # Wait for any zip code input to be available
        print("Waiting for zip code input field...")
        wait = WebDriverWait(driver, 15)
        
        # Take a screenshot to debug
        driver.save_screenshot("initial_page.png")
        print(f"Saved screenshot to initial_page.png")
        
        # Try to find the zip code input field (only using the selector that worked previously)
        print("Looking for ZIP code input field...")
        location_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@placeholder, 'ZIP')]"))
        )
        print("Found ZIP code input field")
            
        # Enter the zipcode
        print(f"Entering zipcode: {zipcode}")
        location_input.clear()
        location_input.send_keys(zipcode)
        
        # Submit using the form submit button (method 5 that worked before)
        print("Submitting zipcode using form button")
        submit_button = driver.find_element(By.XPATH, "//form//button[@type='submit']")
        submit_button.click()
        print("Submission method succeeded")
        
        # Wait for page to react
        time.sleep(3)
        
        # Take a screenshot after submitting zip
        driver.save_screenshot("after_zip_submission.png")
        print(f"Saved screenshot to after_zip_submission.png")
        
        # Check if we successfully navigated to a shopping page
        if "collections" in driver.current_url or "store" in driver.current_url:
            print(f"Successfully set location to zipcode: {zipcode}")
            print(f"Current URL: {driver.current_url}")
            return True
        else:
            print(f"Failed to navigate to shopping page. Current URL: {driver.current_url}")
            return False
        
    except Exception as e:
        print(f"Error setting location: {e}")
        # Take error screenshot
        driver.save_screenshot("location_error.png")
        print(f"Saved error screenshot to location_error.png")
        return False

def handle_popups(driver):
    """Handle any popup dialogs, cookie notices, or modal windows that might appear."""
    try:
        # List of possible selectors for close/accept buttons on popups
        popup_selectors = [
            # Cookie acceptance
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Accept All')]",
            "//button[contains(text(), 'I Accept')]", 
            "//button[contains(text(), 'Agree')]",
            "//button[contains(text(), 'Accept Cookies')]",
            "//button[contains(@class, 'cookie-accept')]",
            "//button[contains(@class, 'cookie-consent')]",
            
            # Modal close buttons
            "//button[contains(@class, 'modal-close')]",
            "//button[contains(@class, 'close-modal')]",
            "//button[contains(@aria-label, 'Close')]",
            "//div[contains(@class, 'modal')]//button[contains(@class, 'close')]",
            "//div[contains(@role, 'dialog')]//button",
            "//button[contains(@class, 'btn-close')]",
            
            # Generic close icons
            "//span[contains(@class, 'close')]",
            "//i[contains(@class, 'close')]",
            "//i[contains(@class, 'fa-times')]"
        ]
        
        # Check for each type of popup and attempt to close it
        for selector in popup_selectors:
            try:
                popup_elements = driver.find_elements(By.XPATH, selector)
                if popup_elements:
                    print(f"Found popup element with selector: {selector}")
                    for element in popup_elements:
                        if element.is_displayed():
                            element.click()
                            print(f"Clicked on popup element with selector: {selector}")
                            time.sleep(1)  # Small delay to let the popup close
            except Exception as e:
                print(f"Error handling popup with selector {selector}: {e}")
        
        return True
    except Exception as e:
        print(f"Error in handle_popups: {e}")
        return False

def scrape_produce_items(driver, max_items=None):
    """Scrape all produce items from the page."""
    produce_url = "https://sameday.costco.com/store/costco/collections/n-produce-50673"
    driver.get(produce_url)
    print(f"Navigated to produce URL: {produce_url}")
    
    # Save HTML for debugging
    html_source = driver.page_source
    with open("produce_page_source.html", "w", encoding="utf-8") as f:
        f.write(html_source)
    print("Saved page source to produce_page_source.html for debugging")
    
    # Handle any popups that might appear
    handle_popups(driver)
    
    # Wait for page to fully load with a longer timeout
    print("Waiting for page to fully load...")
    time.sleep(10)
    
    # Take screenshot for debugging
    driver.save_screenshot("produce_page_loaded.png")
    print("Saved screenshot of produce page after loading")
    
    # Scroll to load all items (lazy loading)
    print("Scrolling to load all products...")
    scroll_attempts = 0
    max_scroll_attempts = 10
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while scroll_attempts < max_scroll_attempts:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print(f"Scrolled down (attempt {scroll_attempts + 1})")
        
        # Wait for new items to load
        time.sleep(3)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Try once more before breaking
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            newer_height = driver.execute_script("return document.body.scrollHeight")
            if newer_height == new_height:
                print("Reached end of page after scrolling")
                break
        
        last_height = new_height
        scroll_attempts += 1
    
    # Take a final screenshot after scrolling
    driver.save_screenshot("after_scrolling.png")
    
    # Based on the provided HTML structure, use these precise selectors
    # Target the structure: <a role="button" href="/store/costco/products/[ID]-[NAME]" class="...">
    product_selectors = [
        "//a[@role='button' and contains(@href, '/store/costco/products/')]",
        "//a[contains(@href, '/store/costco/products/')]",
        "//div[contains(@class, 'e-19idom')]/ancestor::a",
        "//div[contains(@class, 'e-bjn8wh')]/ancestor::a",
        "//span[contains(@class, 'screen-reader-only') and contains(text(), 'Current price:')]/ancestor::a",
        "//img[@data-testid='item-card-image']/ancestor::a"
    ]
    
    products = []
    used_selector = None
    
    for selector in product_selectors:
        try:
            print(f"Trying product selector: {selector}")
            product_elements = driver.find_elements(By.XPATH, selector)
            if product_elements and len(product_elements) > 0:
                print(f"Found {len(product_elements)} products with selector: {selector}")
                products = product_elements
                used_selector = selector
                break
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
    
    if not products:
        print("Could not find any products with our selectors. Saving page for debugging.")
        driver.save_screenshot("no_products_found.png")
        
        # Look for any links that might be products
        print("Looking for any links that might be products...")
        links = driver.find_elements(By.TAG_NAME, "a")
        product_links = [link for link in links if '/products/' in (link.get_attribute('href') or '')]
        
        if product_links:
            print(f"Found {len(product_links)} potential product links")
            products = product_links
        else:
            print("No product links found at all.")
            return []
    
    # First extract basic info from the listing page
    product_list = []
    for i, product in enumerate(products):
        try:
            print(f"Processing product {i+1}/{len(products)} from list page")
            
            # Get the product URL
            item_url = product.get_attribute("href")
            if not item_url.startswith("http"):
                # Convert relative URL to absolute
                if item_url.startswith("/"):
                    base_url = "https://sameday.costco.com"
                    item_url = base_url + item_url
            
            # Get product name from the listing page
            try:
                # First try to find element with class that matches product name
                name_element = product.find_element(By.XPATH, ".//div[contains(@class, 'e-147kl2c')]")
                item_name = name_element.text.strip()
            except:
                try:
                    # Fallback to heading role
                    name_element = product.find_element(By.XPATH, ".//*[@role='heading']")
                    item_name = name_element.text.strip()
                except:
                    # Other fallbacks
                    try:
                        non_price_texts = [el.text for el in product.find_elements(By.XPATH, ".//*[not(contains(text(), '$'))]") if el.text.strip()]
                        if non_price_texts:
                            item_name = max(non_price_texts, key=len).strip()
                        else:
                            item_name = f"Unnamed Product {i+1}"
                    except:
                        item_name = f"Unnamed Product {i+1}"
            
            # Get product price from the listing page
            try:
                price_element = product.find_element(By.XPATH, ".//span[contains(@class, 'screen-reader-only') and contains(text(), 'Current price:')]")
                item_price = price_element.text.strip()
            except:
                try:
                    # Alternative: Look for any text with $ sign
                    price_elements = product.find_elements(By.XPATH, ".//*[contains(text(), '$')]")
                    if price_elements:
                        item_price = price_elements[0].text.strip()
                    else:
                        item_price = "Price not found"
                except:
                    item_price = "Price not found"
            
            # Get product image URL from the listing page
            try:
                # Look for the image with data-testid="item-card-image"
                img_element = product.find_element(By.XPATH, ".//img[@data-testid='item-card-image']")
                
                # Try srcset first, which contains multiple resolution options
                img_srcset = img_element.get_attribute("srcset")
                if img_srcset:
                    # Extract the highest resolution image (usually the 4x version at the end)
                    srcset_parts = img_srcset.split(',')
                    if srcset_parts and len(srcset_parts) >= 4:  # If we have the 4x version
                        # Get the last part which should be the highest resolution
                        highest_res_part = srcset_parts[-1].strip()
                        # Extract the URL part before any whitespace
                        item_img_url = highest_res_part.split(' ')[0].strip()
                    elif srcset_parts:  # If we have at least one part
                        # Take the first part if we don't have multiple resolutions
                        first_part = srcset_parts[0].strip()
                        item_img_url = first_part.split(' ')[0].strip()
                    else:
                        # Fallback to src if srcset parsing fails
                        item_img_url = img_element.get_attribute("src")
                else:
                    # Fallback to src attribute
                    item_img_url = img_element.get_attribute("src")
                    
                # Clean up the image URL if it contains filters or strange formatting
                if item_img_url and "filters:" in item_img_url:
                    # Try to extract the base URL before any filters
                    base_img_url_parts = item_img_url.split("filters:")
                    if len(base_img_url_parts) > 1:
                        # Find the last part that looks like a valid URL
                        for part in reversed(base_img_url_parts):
                            if "http" in part:
                                item_img_url = part[part.find("http"):]
                                break
            except:
                try:
                    # Fallback to any image
                    img_element = product.find_element(By.XPATH, ".//img")
                    item_img_url = img_element.get_attribute("src")
                except:
                    item_img_url = "Image not found"
            
            # Add to our list of products to visit
            product_list.append({
                "name": item_name,
                "url": item_url,
                "image_url": item_img_url,
                "price": item_price,
                "page_position": i+1
            })
            
        except Exception as e:
            print(f"Error extracting basic details for product {i+1}: {e}")
            continue
    
    # If max_items is set, limit the number of products to process
    if max_items and max_items > 0 and len(product_list) > max_items:
        print(f"Limiting to {max_items} products for testing (out of {len(product_list)} found)")
        product_list = product_list[:max_items]
    
    # Now navigate to each product page to get the actual Costco item ID
    items = []
    for i, product_info in enumerate(product_list):
        try:
            print(f"\nVisiting product page {i+1}/{len(product_list)}: {product_info['name']}")
            print(f"URL: {product_info['url']}")
            
            # Navigate to the product page
            driver.get(product_info['url'])
            time.sleep(3)  # Wait for the page to load
            
            # Handle any popups
            handle_popups(driver)
            
            # Extract the actual Costco item ID
            item_id = None
            try:
                # Look for the item ID in the format: <div class="e-16zy4wa">Item: 57554</div>
                id_selectors = [
                    "//div[contains(@class, 'e-16zy4wa')]",
                    "//div[contains(text(), 'Item:')]",
                    "//*[contains(text(), 'Item:')]"
                ]
                
                for id_selector in id_selectors:
                    id_elements = driver.find_elements(By.XPATH, id_selector)
                    for id_element in id_elements:
                        id_text = id_element.text.strip()
                        if "Item:" in id_text:
                            # Extract the numeric ID from "Item: XXXXX"
                            item_id = id_text.split("Item:")[1].strip()
                            print(f"Found item ID: {item_id}")
                            break
                    
                    if item_id:
                        break
                
                # If still not found, try additional methods
                if not item_id:
                    # Try to find any element that might contain the item ID
                    potential_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Item')]")
                    for elem in potential_elements:
                        text = elem.text.strip()
                        if "Item" in text and ":" in text:
                            # Try to extract numeric content after "Item:"
                            parts = text.split(":")
                            if len(parts) > 1:
                                potential_id = parts[1].strip()
                                # Check if it's numeric
                                if potential_id.isdigit():
                                    item_id = potential_id
                                    print(f"Found item ID with alternative method: {item_id}")
                                    break
            
                # If still not found, create a placeholder ID
                if not item_id:
                    print("Could not find item ID on the product page")
                    # Extract ID from URL as fallback
                    url_parts = product_info['url'].split('/')
                    if len(url_parts) > 0:
                        last_part = url_parts[-1]
                        # The ID-like part is before the first dash
                        url_id = last_part.split('-')[0] if '-' in last_part else last_part
                        item_id = f"url-{url_id}"
                    else:
                        item_id = f"unknown-{i+1}"
            
            except Exception as e:
                print(f"Error extracting item ID: {e}")
                # Use URL-based ID as fallback
                url_parts = product_info['url'].split('/')
                if len(url_parts) > 0:
                    last_part = url_parts[-1]
                    url_id = last_part.split('-')[0] if '-' in last_part else last_part
                    item_id = f"url-{url_id}"
                else:
                    item_id = f"unknown-{i+1}"
            
            # Get a high-resolution product image from the detail page
            try:
                # First try to find the main product image on detail page
                detail_img_selectors = [
                    "//img[contains(@alt, 'hero')]",  # Specific selector from the example
                    "//img[contains(@class, 'product-image')]",
                    "//img[contains(@alt, 'product')]"
                ]
                
                detail_img_element = None
                
                # Try each selector
                for detail_selector in detail_img_selectors:
                    detail_img_elements = driver.find_elements(By.XPATH, detail_selector)
                    if detail_img_elements:
                        detail_img_element = detail_img_elements[0]
                        break
                
                if detail_img_element:
                    # Get the highest quality image URL
                    src_url = detail_img_element.get_attribute("src")
                    srcset = detail_img_element.get_attribute("srcset")
                    
                    if srcset:  # Prefer srcset for highest resolution
                        srcset_parts = srcset.split(',')
                        if srcset_parts and len(srcset_parts) >= 4:  # If we have the 4x version
                            # Get the last part which should be the highest resolution
                            highest_res_part = srcset_parts[-1].strip()
                            # Extract the URL part before any whitespace
                            high_res_url = highest_res_part.split(' ')[0].strip()
                            if high_res_url:
                                product_info['image_url'] = high_res_url
                        elif srcset_parts:  # If we have at least one part
                            # Take the first part if we don't have multiple resolutions
                            first_part = srcset_parts[0].strip()
                            img_url = first_part.split(' ')[0].strip()
                            if img_url:
                                product_info['image_url'] = img_url
                    elif src_url:  # Use src if srcset is not available
                        product_info['image_url'] = src_url
                        
                    # Make sure we have a clean URL without truncation issues
                    if product_info['image_url'] and product_info['image_url'].endswith(","):
                        product_info['image_url'] = product_info['image_url'][:-1]
            except Exception as e:
                print(f"Error updating image URL from detail page: {e}")
                # Keep the original image URL
            
            # Add the complete product information to our final list
            items.append({
                "name": product_info['name'],
                "id": item_id,
                "url": product_info['url'],
                "image_url": product_info['image_url'],
                "price": product_info['price']
            })
            
            print(f"Added product with ID {item_id}: {product_info['name']} - {product_info['price']}")
            print(f"Image URL: {product_info['image_url']}")
            
        except Exception as e:
            print(f"Error processing product detail page {i+1}: {e}")
            # Still add the product with the information we have
            items.append({
                "name": product_info['name'],
                "id": f"error-{i+1}",
                "url": product_info['url'],
                "image_url": product_info['image_url'],
                "price": product_info['price']
            })
    
    return items

def save_to_csv(items, filename="costco_produce_items.csv"):
    """Save the scraped items to a CSV file."""
    fieldnames = ["name", "id", "url", "image_url", "price"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    print(f"Data saved to {filename}")
    print(f"Total items: {len(items)}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Costco Sameday Crawler')
    parser.add_argument('--visible', action='store_true', help='Run in visible mode (not headless)')
    parser.add_argument('--zipcode', type=str, default='94107', help='ZIP code for delivery location')
    parser.add_argument('--output', type=str, default='costco_produce_items.csv', help='Output CSV filename')
    parser.add_argument('--max', type=int, default=0, help='Maximum number of items to crawl (for testing, 0 = no limit)')
    args = parser.parse_args()
    
    # Generate filename with zipcode and date
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if args.output == 'costco_produce_items.csv':  # Only modify the default filename
        filename = f"costco_produce_items_{args.zipcode}_{today_date}.csv"
    else:
        # If user specified custom filename, use that
        filename = args.output
    
    print(f"Running with settings: visible={not args.visible}, zipcode={args.zipcode}, output={filename}, max_items={args.max}")
    
    driver = setup_driver(headless=not args.visible)
    try:
        # Take screenshot of the initial state
        driver.get("https://sameday.costco.com")
        time.sleep(3)
        driver.save_screenshot("before_location.png")
        print("Took screenshot of initial state")
        
        # Handle any initial popups before setting location
        handle_popups(driver)
        
        if not set_location(driver, zipcode=args.zipcode):
            print("Failed to set location. Exiting.")
            return
        
        # Handle any popups after setting location
        handle_popups(driver)
        
        items = scrape_produce_items(driver, max_items=args.max)
        if items:
            save_to_csv(items, filename=filename)
        else:
            print("No items found to save.")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main() 