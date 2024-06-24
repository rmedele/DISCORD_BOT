import requests
from Tokens import API_FOOTBALL_KEY  # Ensure you have your API key here

def fetch_live_matches():
    url = 'https://v3.football.api-sports.io/fixtures?live=all'
    headers = {'x-apisports-key': API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def print_raw_data():
    data = fetch_live_matches()
    if data:
        print("Raw API response:")
        print(data)
    else:
        print("Failed to fetch data from API. Check your API key and network connection.")

# Run the function to print raw data
if __name__ == "__main__":
    print_raw_data()