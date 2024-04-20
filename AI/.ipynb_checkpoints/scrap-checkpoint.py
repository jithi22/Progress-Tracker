import requests
from bs4 import BeautifulSoup
import re

# import snoop
# @snoop
def scrapper():
    url = 'https://en.wikipedia.org/wiki/Artificial_intelligence'
    
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
        
        # print(words)
        with open('AI.txt', 'w', encoding='utf-8') as file:
            file.write(' '.join(words))
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

scrapper()
