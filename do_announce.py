"""
向订阅用户发布通知
"""


from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import pack_message, pack_text_data

from group_bot.config import DB_NAME, HTTP_ZEROMESH, MIXIN_BOT_KEYSTORE
from group_bot.models import BotDB

config = AppConfig.from_payload(MIXIN_BOT_KEYSTORE)
db = BotDB(DB_NAME)
xin = HttpClient_AppAuth(config, api_base=HTTP_ZEROMESH)
users = db.get_all_rss_users()

text = """通知内容文本
可以多行
"""

packed = pack_text_data(text)

for user_id in users:
    print("send to user: ", user_id)
    cid = xin.get_conversation_id_with_user(user_id)
    msg = pack_message(packed, cid)
    resp = xin.api.send_messages(msg)
    if "data" in resp:
        print(resp["data"]["message_id"], user_id)
