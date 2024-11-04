import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')

TOKEN = os.getenv('TOKEN')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

PRICE = os.getenv('PRICE')

# moscow_tz = pytz.timezone('Europe/Moscow')
# now_in_moscow = datetime.now(moscow_tz)
