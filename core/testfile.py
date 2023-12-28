import os
from dotenv import load_dotenv

load_dotenv()  # This line brings all environment variables from .env into os.environ
SERVER_URL = os.environ['SERVER_URL']
TEMP_SITE = os.environ['TEMP_SITE']

print(SERVER_URL)
print(TEMP_SITE)