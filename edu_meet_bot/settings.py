import os
from dotenv import load_dotenv
from pathlib import Path
from edu_meet_bot.utils import get_external_ip


load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')

TOKEN = os.getenv('TOKEN')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
PRODUCTION = os.getenv('PRODUCTION', 'False') == 'True'

PRICE = os.getenv('PRICE')


BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_files')

TUTOR_PHOTO = os.getenv('TUTOR_PHOTO')
TUTOR_TG_ID = int(os.getenv('TUTOR_TG_ID'))
ABOUT_MASSAGE = os.getenv('ABOUT_MASSAGE')


SUPPORT_CHAT_ID = os.getenv('SUPPORT_CHAT_ID')

# webhook settings
WEBHOOK_PATH = "/send_notification"
WEBHOOK_PORT = 9000

if PRODUCTION:
    WEBHOOK_HOST = get_external_ip()
