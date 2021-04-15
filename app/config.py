import os

DATABASE_URI = 'sqlite:///database.db'
HOST = '0.0.0.0'
PORT = int(os.environ.get("PORT", 8080))

HTML_DIR = 'app/templates'

google_client = os.getenv('GOOGLE_CLIENT')
google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')

MAX_SOLD_OUT_POST_PER_DAY = 10
MAX_CONGESTION_POST_PER_DAY = 10
