import requests
from dotenv import load_dotenv
import os, logging

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')


HEADERS = { "Authorization": f'Bearer {API_TOKEN}'}

logger = logging.getLogger(__name__)

def call_api(url):
    try:
        resp = requests.get("https://api.clashroyale.com/v1/" + url, headers = HEADERS)
        resp.raise_for_status() # Catch auth errors/maintenance
        return resp.json()
    except requests.RequestException as exc:
        logger.error(f"API request to {url} failed: {exc}")

        if "invalidIp" in resp.text:
            logger.error(f"{resp.json().get('message', 'Invalid IP address.')} Check your API token.")
        return None