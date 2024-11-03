import os
from dotenv import load_dotenv
from databases import Database
# import pytz
# from datetime import datetime


DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')

load_dotenv()

TOKEN = os.getenv('TOKEN')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

PRICE = os.getenv('PRICE')

db = Database(DATABASE_URL)

# moscow_tz = pytz.timezone('Europe/Moscow')
# now_in_moscow = datetime.now(moscow_tz)
