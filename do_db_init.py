from group_bot.config import DB_NAME
from group_bot.models import BotDB

db = BotDB(DB_NAME, init=True)
