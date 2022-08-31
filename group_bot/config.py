import os

from mininode.utils import decode_seed_url

from group_bot import config_private as PVT

HTTP_DEFAULT = "https://api.mixin.one"
HTTP_ZEROMESH = "https://mixin-api.zeromesh.net"
BLAZE_DEFAULT = "wss://blaze.mixin.one"
BLAZE_ZEROMESH = "wss://mixin-blaze.zeromesh.net"

DEV_MIXIN_ID = PVT.DEV_MIXIN_ID
RSS_MIXIN_ID = PVT.RSS_MIXIN_ID
MIXIN_BOT_KEYSTORE = PVT.MIXIN_BOT_KEYSTORE

DB_NAME = f"sqlite:///{os.path.dirname(os.path.dirname(__file__))}/rss_bot.db"

RUM_SEED_URL = PVT.RUM_SEED_URL

# fake data for test, please update: create the group and get the group info.
COMMON_ACCOUNT_PWD = PVT.COMMON_ACCOUNT_PWD
MINUTES = -30
TEXT_LENGTH_MIN = 6
TEXT_LENGTH_MAX = 5000
GROUP_NAME = decode_seed_url(RUM_SEED_URL)["group_name"]

WELCOME_TEXT = f"""👋 hello, I am a bot. 致力于让 mixin 用户更方便地参与到 Rum 种子网络之中。

如果您直接在聊天框向我发送文本或图片，我将为您映射并托管一个密钥账号，帮您把内容发送到 RUM 种子网络 {GROUP_NAME}。您也将自动订阅该种子网络的动态推送。
"""
