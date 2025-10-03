import requests,urllib
from dotenv import load_dotenv
import os, logging

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
CLAN_NAME = os.getenv('CLAN_NAME')

HEADERS = { "Authorization": f'Bearer {API_TOKEN}'}

def call_api(url):
    return requests.get(url, headers = HEADERS)