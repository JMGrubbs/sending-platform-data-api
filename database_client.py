from settings import ANALYTICS_CONNECTION
from databases import Database

db_client = Database(ANALYTICS_CONNECTION, min_size=2, max_size=20)
