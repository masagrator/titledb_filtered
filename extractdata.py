import requests
import json
import os
from pathlib import Path

# Create the scrap folder if it doesn't exist
os.makedirs("scrap", exist_ok=True)

# API details
base_url = "https://store-jp.nintendo.com/mobify/proxy/api/product/shopper-products/v1/organizations/f_ecom_bfgj_prd/products/"
product_id_start = 70010000096867
product_id_end = 70010000100000  # Adjust this range as needed

# Authorization token
headers = {
    "Authorization": "Bearer eyJ2ZXIiOiIxLjAiLCJqa3UiOiJzbGFzL3Byb2QvYmZnal9wcmQiLCJraWQiOiJjNTlkMTQxMS0yZTdlLTQ1NTktYTRlYy01ODE1MTJiN2MzZmUiLCJ0eXAiOiJqd3QiLCJjbHYiOiJKMi4zLjQiLCJhbGciOiJFUzI1NiJ9.eyJhdXQiOiJHVUlEIiwic2NwIjoic2ZjYy5zaG9wcGVyLW15YWNjb3VudC5iYXNrZXRzIHNmY2Muc2hvcHBlci1kaXNjb3Zlcnktc2VhcmNoIHNmY2Muc2hvcHBlci1wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnJ3IHNmY2Muc2hvcHBlci1jdXN0b21lcnMubG9naW4gc2ZjYy5zaG9wcGVyLWV4cGVyaWVuY2Ugc2ZjYy5zaG9wcGVyLWJhc2tldHMtb3JkZXJzIHNmY2Muc2hvcHBlci1jdXN0b21lcnMucmVnaXN0ZXIgc2ZjYy5wcm9kdWN0cyBzZmNjLnNob3BwZXItbXlhY2NvdW50LmFkZHJlc3Nlcy5ydyBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cy5ydyBzZmNjLnNob3BwZXItcHJvZHVjdGxpc3RzIHNmY2Muc2hvcHBlci1wcm9tb3Rpb25zIHNmY2Muc2Vzc2lvbl9icmlkZ2Ugc2ZjYy5zaG9wcGVyLWJhc2tldHMtb3JkZXJzLnJ3IHNmY2Muc2Vzc2lvbl9icmlkZ2VzZmNjLnNob3BwZXItbXlhY2NvdW50LmFkZHJlc3NlcyBzZmNjLnNob3BwZXItZ2lmdC1jZXJ0aWZpY2F0ZXMgc2ZjYy5zaG9wcGVyLW15YWNjb3VudC5wYXltZW50aW5zdHJ1bWVudHMucncgY19wd2FfciBzZmNjLnNob3BwZXItbXlhY2NvdW50Lm9yZGVyc3NmY2Muc2hvcHBlci1teWFjY291bnQucGF5bWVudGluc3RydW1lbnRzIHNmY2Muc2hvcHBlci1wcm9kdWN0LXNlYXJjaCBzZmNjLnNob3BwZXItbXlhY2NvdW50LnByb2R1Y3RsaXN0cyBzZmNjLnNob3BwZXItY2F0ZWdvcmllcyBzZmNjLnNob3BwZXItbXlhY2NvdW50Iiwic3ViIjoiY2Mtc2xhczo6YmZnal9wcmQ6OnNjaWQ6MWVjNjk5MWEtMWU4ZS00YzA3LWJjNWMtOGZjOTRhMWE2MTI3Ojp1c2lkOmNjYWVjYWMwLWEzYWEtNDczMy1iYzU5LTI4NjU5OGE2MDFjMCIsImN0eCI6InNsYXMiLCJpc3MiOiJzbGFzL3Byb2QvYmZnal9wcmQiLCJpc3QiOjEsImRudCI6IjAiLCJhdWQiOiJjb21tZXJjZWNsb3VkL3Byb2QvYmZnal9wcmQiLCJuYmYiOjE3NjgxMTc0NTAsInN0eSI6IlVzZXIiLCJpc2IiOiJ1aWRvOm5pbnRlbmRvOjp1cG46YzUxY2FjYjU3YTI1ZDIyMTo6dWlkbjpNYXNhR3JhdG9SIE1hc2FHcmF0b1I6OmdjaWQ6YmN3MGxGeHVsRndYYVJ3cmxGd3FZWWxYa1g6OnJjaWQ6YWIxQ2kyQXJNa2tFVWhLd1J2blo5U3hZZFc6OmNoaWQ6TU5TIiwiZXhwIjoxNzY4MTE5MjgwLCJpYXQiOjE3NjgxMTc0ODAsImp0aSI6IkMyQzcyNjQ3NzY5NDAtMTY0OTgyMTM5NTEwNDI2OTMxMzk2NzgzMjkwIn0.DmXYaRtG2A0HJH9FTBXO_6IXgKDTR1zcf2kabuut4GHBl1F-cNoj-l_sxsDv8bBws_po-1EolUB3sMZD0hDBww"
}

params = {
    "currency": "JPY",
    "locale": "ja-JP",
    "siteId": "MNS"
}

print(f"Starting scraper from {product_id_start} to {product_id_end}...")
successful_requests = 0
failed_requests = 0

for product_id in range(product_id_start, product_id_end + 1):
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