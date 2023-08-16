import requests
from bs4 import BeautifulSoup
import re

def get_industry(naics_code: int):

    base_url = "https://www.naics.com/naics-code-description/?code="
    url = base_url + str(int(naics_code))

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title').get_text()

        pattern = r'NAICS Code: \d+ (.*?) \| NAICS Association'
        match = re.search(pattern, title)
        if match:
            return match.group(1)

    except requests.exceptions.RequestException as e:
        print("Error making request:", e)
        