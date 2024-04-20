import json
import requests
from bs4 import BeautifulSoup
import re

# Path to your JSON file
file_path = 'academics.json'

# Load the JSON file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Count the number of items
# Assuming the JSON file contains a list of objects
item_count = len(data)

print(f'Number of items in the JSON file: {item_count}')

def scrapper(url, title):
    url = 'https://en.wikipedia.org' + url
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the main content of the article
        html_content = soup.find('div', {'class': 'mw-content-container'})
        
        # Extract text
        text_only = html_content.get_text() if html_content else ""
        
        # Remove non-alphanumeric characters except spaces
        clean_text = re.sub(r'[^a-zA-Z\s]', '', text_only)
        
        # Remove words less than 4 characters and split into words
        words = [word for word in clean_text.split() if ( len(word) >= 4 and len(word) <= 15) ]
        
        with open(title, 'w', encoding='utf-8') as file:
            file.write(' '.join(words))
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
# data = data[:10]        
import time
import sys

start_time = time.time()  # Record the start time of the process
total_items = len(data)  # Total number of items to process

for index, dat in enumerate(data):
    print(dat)
    scrapper(dat['href'], 'store/'+dat['title']+'.txt')  # Your scrapping function
    
    # Calculate progress
    items_processed = index + 1
    progress_percentage = (items_processed / total_items) * 100

    # Calculate time elapsed and estimate remaining time
    time_elapsed = time.time() - start_time
    time_per_item = time_elapsed / items_processed
    estimated_time_remaining = time_per_item * (total_items - items_processed)

    # Update progress display
    sys.stdout.write(f"\rProgress: {items_processed}/{total_items} items ({progress_percentage:.2f}%) - Estimated time remaining: {estimated_time_remaining:.2f} seconds")
    sys.stdout.flush()

# Move to the next line after completion
print()

