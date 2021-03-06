import os
import uuid

DATABASE_URI = 'sqlite:///database.db'
HOST = '0.0.0.0'
PORT = int(os.environ.get("PORT", 8080))

HTML_DIR = 'app/templates'

MAX_SOLD_OUT_POST_PER_DAY = 10
MAX_CONGESTION_POST_PER_DAY = 10

IS_LOCAL = os.path.exists('.idea')

NAMESPACE = uuid.UUID('c52d908a-8a4d-5c99-b537-14379f70fdeb')

IS_SSL = False