import datetime
import time

from group_bot import RumBot

bot = RumBot()
while True:
    try:
        bot.send_to_rum()  # 帮 xin 用户代发内容到 Rum
        time.sleep(1)
    except Exception as e:
        print(datetime.datetime.now(), "send_to_rum failed", e)
        time.sleep(3)
