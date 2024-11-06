import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')

TOKEN = os.getenv('TOKEN')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

PRICE = os.getenv('PRICE')


BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_files')

TUTOR_PHOTO = os.getenv('TUTOR_PHOTO')
ABOUT_MASSAGE = os.getenv('ABOUT_MASSAGE')