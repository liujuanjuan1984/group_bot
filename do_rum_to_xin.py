import datetime
import time

from group_bot import RumBot

bot = RumBot(init=True, echo=False)
while True:
    try:
        print(datetime.datetime.now(), "send_group_msg_to_xin ...")
        bot.send_group_msg_to_xin()  # Rum 动态转发到 xin
        time.sleep(1)

    except Exception as e:
        print(datetime.datetime.now(), "send_group_msg_to_xin failed", e)
        time.sleep(3)
    try:
        print(datetime.datetime.now(), "get_group_trxs ...")
        bot.get_group_trxs(without_timestamp=True)
        time.sleep(1)
    except Exception as e:
        print(datetime.datetime.now(), "get_group_trxs failed", e)
        time.sleep(3)
