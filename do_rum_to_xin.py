import datetime
import time

from group_bot import RumBot

bot = RumBot()
while True:
    try:
        bot.send_group_msg_to_xin()  # Rum 动态转发到 xin
        time.sleep(1)
    except Exception as e:
        print(datetime.datetime.now(), "send_group_msg_to_xin failed", e)
        time.sleep(3)
