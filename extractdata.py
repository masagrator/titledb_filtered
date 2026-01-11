import requests
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Authorization token
glob_headers = {}

call = 0

def scrape_with_selenium():
    """Uses Selenium to load the page and monitor network requests"""
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    
    # Setup Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless mode
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Disable cache
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disk-cache-size=0")
    
    # Enable logging to capture network activity
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except ImportError:
        driver = webdriver.Chrome(options=chrome_options)
        
    # Enable network tracking and disable cache via DevTools
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})
    
    try:
        print("Loading page...")
        # Add this before driver.get() in the try block:
        driver.delete_all_cookies()
        driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        if (call == 0): driver.get("https://store-jp.nintendo.com/item/software/D70010000083295")
        else if (call == 1): driver.get("https://store-jp.nintendo.com/item/software/D70010000089960")
        else if (call == 2): driver.get("https://store-jp.nintendo.com/item/software/D70010000096867")
        if (call == 2):
            call = 0
        else call += 1
        # Wait for the API call to be made
        WebDriverWait(driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )

        time.sleep(3)
        
        # Get performance logs (network requests)
        logs = driver.get_log('performance')
        
        auth_headers = []

        # After getting logs, before the loop:
        print(f"Total performance logs captured: {len(logs)}")
        api_calls_found = sum(1 for log in logs if 'shopper-products' in str(log))
        print(f"API calls containing 'shopper-products': {api_calls_found}")

        for log in logs:
            try:
                message = json.loads(log['message'])['message']
                
                # Look for network requests
                if message['method'] == 'Network.responseReceived':
                    request_id = message['params']['requestId']
                    url = message['params']['response']['url']
                    
                    # Check if this is the API endpoint we're looking for
                    if 'shopper-products' in url:
                        print(f"\n✓ Found API call: {url}")
                        
                        # Try to get request details
                        try:
                            request_body = driver.execute_cdp_cmd('Network.getRequestPostData', {'requestId': request_id})
                            print(f"Response body available")
                        except:
                            pass
                
                # Look for request headers
                if message['method'] == 'Network.requestWillBeSent':
                    url = message['params']['request']['url']
                    if 'shopper-products' in url:
                        headers = message['params']['request']['headers']
                        if 'Authorization' in headers:
                            auth_headers.append(headers['Authorization'])
                            print(f"\n✓ Authorization Header Found!")
                            print(f"Authorization: {headers['Authorization'][:50]}...")
                            
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
        if not auth_headers:
            print("No Authorization header found in network logs!")
            return glob_headers["Authorization"]
        
        return auth_headers[0]
    
    finally:
        driver.quit()

tree = ET.parse('switch.xml')
root = tree.getroot()

NSUIDs = []

for title in root.findall('TitleInfo'):
    link = title.find('LinkURL').text
    
    nsuID = link.replace("/titles/", "")

    if nsuID not in NSUIDs:
        NSUIDs.append(nsuID)

# Create the scrap folder if it doesn't exist
os.makedirs("scrap", exist_ok=True)

# API details
base_url = "https://store-jp.nintendo.com/mobify/proxy/api/product/shopper-products/v1/organizations/f_ecom_bfgj_prd/products/"

params = {
    "currency": "JPY",
    "locale": "ja-JP",
    "siteId": "MNS"
}

print(f"Starting scraper...")
successful_requests = 0
failed_requests = 0

glob_headers["Authorization"] = scrape_with_selenium()

i = 0
error_count = 0
max_error_count = 30

while(i < len(NSUIDs)):
    product_id = NSUIDs[i]
    try:
        # Construct the URL with the current product ID
        url = f"{base_url}{product_id}"
        
        # Make the request
        response = requests.get(url, headers=glob_headers, params=params, timeout=30)
        
        # Check if the response is successful (HTTP 200)
        if response.status_code == 200:
            # Save the JSON response to a file
            file_path = os.path.join("scrap", f"{product_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)
            
            successful_requests += 1
            print(f"✓ Product {product_id} - HTTP 200 - Saved to {file_path}")
            i += 1
        elif response.status_code != 404:
            print(f"✗ Bearer is dead, renewing bearer...")
            glob_headers["Authorization"] = scrape_with_selenium()
            error_count += 1
            if (error_count > max_error_count): break
        else:
            failed_requests += 1
            print(f"✗ Product {product_id} - HTTP {response.status_code}")
            i += 1
    
    except requests.exceptions.Timeout:
        error_count += 1
        print(f"✗ Product {product_id} - Timeout error")
        if (error_count > max_error_count): break
    
    except requests.exceptions.RequestException as e:
        error_count += 1
        print(f"✗ Product {product_id} - Request error: {e}")
        if (error_count > max_error_count): break
    
    except json.JSONDecodeError:
        error_count += 1
        print(f"✗ Product {product_id} - Invalid JSON response")
        if (error_count > max_error_count): break
    
    except Exception as e:
        error_count += 1
        print(f"✗ Product {product_id} - Error: {e}")
        if (error_count > max_error_count): break

print(f"\n--- Summary ---")
print(f"Successful requests (HTTP 200): {successful_requests}")
print(f"Failed requests: {failed_requests}")
print(f"Total: {successful_requests + failed_requests}")



