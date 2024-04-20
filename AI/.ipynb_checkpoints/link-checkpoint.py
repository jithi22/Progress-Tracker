import requests
from bs4 import BeautifulSoup
import re
import json

# import snoop
# @snoop
def scrapper():
    url = 'https://en.wikipedia.org/wiki/List_of_academic_fields'
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Locate the main content of the article
        html_content = soup.select('li a')
        print("===================>",len(html_content))
        # Extract text
        text_only = [{'title': html.get('title'), 'href': html.get('href')} for html in html_content if html.get('title') and html.get('href')]
        # print(text_only)
        # # Remove non-alphanumeric characters except spaces
        # clean_text = re.sub(r'[^a-zA-Z\s]', '', text_only)
        
        # # Remove words less than 4 characters and split into words
        # words = [word for word in clean_text.split() if ( len(word) >= 4 and len(word) <= 15) ]
        
        with open('academics.json', 'w', encoding='utf-8') as file:
            json.dump(text_only, file, ensure_ascii=False, indent=4)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

scrapper()
