import pandas as pd
import requests
import sqlite3
from io import StringIO
import random

class dataset:

    def __init__(self, package_name):
        base_url = "https://data.sba.gov/api/3/action/package_show?id="
        self.send_api_request(base_url + package_name)
        self.db_path  = "data/SBA_local.db"
        self.package_name = package_name

    def send_api_request(self, api_url):
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            self.response =  response.json()
        except requests.exceptions.RequestException as e:
            print("Error making API request:", e)
        
    def fetch_csv(self):
        conn = sqlite3.connect(self.db_path )

        # File download wait messages
        print("Initiating file download...")
        messages = [
            "Blending into the digital savannah...",
            "Gathering stardust for your downloads...",
            "Darkening camouflage mode for faster data absorption...",
            "Summoning the download spirits...",
            "Finding a branch for a tail anchor...",
            "Convincing the meerkat to run faster...",
            "Focusing disconjugate disco balls for eyes...",
            "Downloading files... or is it uploading happiness?",
            "Leaning in for a shot and a prayer...",
            "Tuning up the tongue catapult...",
            "Catching fireflies for the download jar...",
        ]
        max_length = 0
        for message in messages:
            message_length = len(message)
            if message_length > max_length:
                max_length = message_length

        for resource in self.response['result']['resources']:

            if resource['format'].lower() == "csv":
                message = random.choice(messages)
                message += ' '*(max_length - len(message))
                print(message, end='\r', flush=True)

                response = requests.get(resource['url'])
                csv_data = response.text
                
                # Append the DataFrame to the SQLite database
                df = pd.read_csv(StringIO(csv_data))
                df.to_sql(self.response['result']['name'], conn, if_exists='append', index=False)

        print("\nAll files downloaded!")
        conn.close()

    def get_rows(self, conditions_dict: dict, table_name=None) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)

        if table_name is None:
            table_name = self.package_name

        # Generate query from conditions
        conditions = []
        values = []
        for column, value in conditions_dict.items():
            conditions.append(f"{column} LIKE ?")
            values.append(f"{value}")

        query = f"SELECT * FROM '{table_name}' WHERE {' AND '.join(conditions)}"

        result = pd.read_sql_query(query, conn, params=values)
        conn.close()

        return result
    
    def list_packages() -> list:
        try:
            url = "https://data.sba.gov/api/3/action/package_list"
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            return response.json()['result']
        
        except requests.exceptions.RequestException as e:
            print("Error making API request:", e)

