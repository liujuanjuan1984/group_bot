import os

from mininode.utils import decode_seed_url

from group_bot import config_private as PVT

HTTP_DEFAULT = "https://api.mixin.one"
HTTP_ZEROMESH = "https://mixin-api.zeromesh.net"
BLAZE_DEFAULT = "wss://blaze.mixin.one"
BLAZE_ZEROMESH = "wss://mixin-blaze.zeromesh.net"

DEV_MIXIN_ID = PVT.DEV_MIXIN_ID
MIXIN_BOT_KEYSTORE = PVT.MIXIN_BOT_KEYSTORE

DB_NAME = f"sqlite:///{os.path.dirname(os.path.dirname(__file__))}/rss_bot.db"

RUM_SEED_URL = PVT.RUM_SEED_URL

USER_CAN_SEND_CONTENT = PVT.USER_CAN_SEND_CONTENT
IS_LIKE_TRX_SENT_TO_USER = PVT.IS_LIKE_TRX_SENT_TO_USER

# the pttn and repl for re.sub to replace the text in the message.
RE_PAIRS = PVT.RE_PAIRS

# fake data for test, please update: create the group and get the group info.
COMMON_ACCOUNT_PWD = PVT.COMMON_ACCOUNT_PWD
MINUTES = -30
TEXT_LENGTH_MIN = 6
TEXT_LENGTH_MAX = 5000
GROUP_NAME = decode_seed_url(RUM_SEED_URL)["group_name"]

_text = "当您直接在聊天框发送文本或图片，" if USER_CAN_SEND_CONTENT else "当您引用并回复一条动态，"
WELCOME_TEXT = f"""👋 hello, I am a group bot. 致力于让 mixin 用户更方便地参与到 Rum 种子网络之中。

如何使用？

1. {_text}bot 将为您映射并托管一个密钥账号，帮您把内容发送到 RUM 种子网络 {GROUP_NAME}。
2. 当您与 bot 互动后，您将自动订阅该种子网络的动态推送。您也可以发送“订阅动态” （不包含引号）来订阅，发送“取消订阅” （不包含引号）来取消订阅。
3. 当您回复任意一条动态，bot 将为您搜寻该动态所对应的 trx，并把您的回复发送到相应的 trx 之下。

特别规则：
1. 如果您直接在聊天框发送 “修改昵称:我是bot”或“修改昵称：我是bot” （不包含引号），bot 将自动帮您修改 rum 账号的昵称为：我是bot
2. 如果您回复一条动态的文本是 “1” （不包含引号）将在 rum 中处理为点赞，回复文本是 “0” （不包含引号）处理为点踩。
3. 如果您直接在聊天框发送 “更换密钥 0xxxxx”（不包含引号，密钥以0x开头，共66位，为 eth 兼容的私钥），可以更换身份为指定的密钥。特别留意，该方式仅为方便用户重置身份，或统一自己在多个种子网络的身份，由此操作后，该密钥不再 100% 安全，该密钥不应该持有任何价值资产。
"""
