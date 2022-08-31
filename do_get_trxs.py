import datetime
import time

from group_bot import RumBot

bot = RumBot()
while True:
    try:
        bot.get_group_trxs()
        time.sleep(1)
    except Exception as e:
        print(datetime.datetime.now(), "get_group_trxs failed", e)
        time.sleep(3)
