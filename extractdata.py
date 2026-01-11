import requests
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

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

# Authorization token
headers = {
    "Authorization": "Bearer eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmZnal9wcmQiLCJraWQiOiJjNTlkMTQxMS0yZTdlLTQ1NTktYTRlYy01ODE1MTJiN2MzZmUiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1kaXNjb3Zlcnktc2VhcmNoIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLWV4cGVyaWVuY2Ugc2ZjYy5zaG9wcGVyLWJhc2tldHMtb3JkZXJzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMucmVnaXN0ZXIgc2ZjYy5wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LmFkZHJlc3Nlcy5ydyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cy5ydyBzZmNjLnNob3BwZXItcHJvZHVjdGxpc3RzIHNmY2Muc2hvcHBlci1wcm9tb3Rpb25zIHNmY2Muc2Vzc2lvbl9icmlkZ2Ugc2ZjYy5zaG9wcGVyLWJhc2tldHMtb3JkZXJzLnJ3IHNmY2Muc2Vzc2lvbl9icmlkZ2VzZmNjLnNob3BwZXItbXlhY2NvdW50LmFkZHJlc3NlcyBzZmNjLnNob3BwZXItZ2lmdC1jZXJ0aWZpY2F0ZXMgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wYXltZW50aW5zdHJ1bWVudHMucncgY19wd2FfciBzZmNjLnNob3BwZXItbXlhY2NvdW50Lm9yZGVyc3NmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1wcm9kdWN0LXNlYXJjaCBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50Iiwic3ViIjoiY2Mtc2xhczo6YmZnal9wcmQ6OnNjaWQ6MWVjNjk5MWEtMWU4ZS00YzA3LWJjNWMtOGZjOTRhMWE2MTI3Ojp1c2lkOjY3ZTljZTgwLWQxNTktNDZhOS05ZTg1LTJjZWYzNDBmNmMyNyIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmZnal9wcmQiLCJpc3QiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmZnal9wcmQiLCJuYmYiOjE3NjgxMjE2OTEsInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOnNsYXM6OnVwbjpHdWVzdDo6dWlkbjpHdWVzdCBVc2VyOjpnY2lkOmJjbEhCSm11bEptYmFSeGJjWm1xWVlsS2MzOjpjaGlkOk1OUyIsImV4cCI6MTc2ODEyMzUyMSwiaWF0IjoxNzY4MTIxNzIxLCJqdGkiOiJDMkM3MjY0Nzc2OTQwLTE2NDk4MjEzOTUxMDQzMTA4MzY0MDcxNjQ3MyJ9.il6DUByuYrxRe4MU45OwoEK94rHNFfxQm6lAd75momDIY0StvK-W9Q9esmWLuFMvvnSAEZ9CyrfICWMJ79wb2w"
}

params = {
    "currency": "JPY",
    "locale": "ja-JP",
    "siteId": "MNS"
}

print(f"Starting scraper...")
successful_requests = 0
failed_requests = 0

for product_id in NSUIDs:
    try:
        # Construct the URL with the current product ID
        url = f"{base_url}{product_id}"
        
        # Make the request
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # Check if the response is successful (HTTP 200)
        if response.status_code == 200:
            # Save the JSON response to a file
            file_path = os.path.join("scrap", f"{product_id}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(response.json(), f, ensure_ascii=False, indent=2)
            
            successful_requests += 1
            print(f"✓ Product {product_id} - HTTP 200 - Saved to {file_path}")
        elif response.status_code == 401:
            print(f"✗ Bearer is dead, cancelling...")
            break
        else:
            failed_requests += 1
            print(f"✗ Product {product_id} - HTTP {response.status_code}")
    
    except requests.exceptions.Timeout:
        failed_requests += 1
        print(f"✗ Product {product_id} - Timeout error")
    
    except requests.exceptions.RequestException as e:
        failed_requests += 1
        print(f"✗ Product {product_id} - Request error: {e}")
    
    except json.JSONDecodeError:
        failed_requests += 1
        print(f"✗ Product {product_id} - Invalid JSON response")
    
    except Exception as e:
        failed_requests += 1
        print(f"✗ Product {product_id} - Error: {e}")

print(f"\n--- Summary ---")
print(f"Successful requests (HTTP 200): {successful_requests}")
print(f"Failed requests: {failed_requests}")
print(f"Total: {successful_requests + failed_requests}")
