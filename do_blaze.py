import datetime
import json
import logging

import requests
from mininode import MiniNode
from mininode.utils import get_filebytes
from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_contact_data, pack_message, pack_text_data
from mixinsdk.utils import parse_rfc3339_to_datetime

from group_bot.config import *
from group_bot.models import BotDB

logger = logging.getLogger(__name__)


class BlazeBot:
    def __init__(self):
        self.config = AppConfig.from_payload(MIXIN_BOT_KEYSTORE)
        self.db = BotDB(DB_NAME)
        self.rum = MiniNode(RUM_SEED_URL)
        self.xin = HttpClient_AppAuth(self.config, api_base=HTTP_ZEROMESH)


def message_handle_error_callback(error, details):
    logger.error("===== error_callback =====")
    logger.error(f"error: {error}")
    logger.error(f"details: {details}")


async def message_handle(message):

    global bot
    action = message["action"]

    # messages sent by bot
    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        logger.info("Mixin blaze server: received the message")

    if action == "LIST_PENDING_MESSAGES":
        logger.info("Mixin blaze server: list pending message")

    if action == "ERROR":
        logger.warning(message["error"])

    if action != "CREATE_MESSAGE":
        return

    error = message.get("error")
    if error:
        logger.info(str(error))
        return

    msg_data = message.get("data", {})

    msg_id = msg_data.get("message_id")
    if not msg_id:
        await bot.blaze.echo(msg_id)
        return

    msg_type = msg_data.get("type")
    if msg_type != "message":
        await bot.blaze.echo(msg_id)
        return

    # 和 server 有 -8 时差。-32 也就是只处理 24 小时内的 message
    create_at = parse_rfc3339_to_datetime(msg_data.get("created_at"))
    blaze_for_hour = datetime.datetime.now() + datetime.timedelta(hours=-32)
    if create_at <= blaze_for_hour:
        await bot.blaze.echo(msg_id)
        return

    msg_cid = msg_data.get("conversation_id")
    if not msg_cid:
        await bot.blaze.echo(msg_id)
        return

    data = msg_data.get("data")
    if not (data and type(data) == str):
        await bot.blaze.echo(msg_id)
        return

    category = msg_data.get("category")
    to_send_data = None
    reply_text = ""
    reply_msgs = []

    if category not in ["PLAIN_TEXT", "PLAIN_IMAGE"]:
        reply_text = f"暂不支持此类消息，如有需求，请联系开发者\ncategory: {category}"
        reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
    elif category == "PLAIN_TEXT":
        msgview = MessageView.from_dict(msg_data)
        _text_length = f"文本长度需在 {TEXT_LENGTH_MIN} 至 {TEXT_LENGTH_MAX} 之间"
        if len(msgview.data_decoded) <= TEXT_LENGTH_MIN:
            reply_text = f"消息太短，无法处理。{_text_length}"
            reply_msgs.append(pack_message(pack_contact_data(RSS_MIXIN_ID), msg_cid))
        elif len(msgview.data_decoded) >= TEXT_LENGTH_MAX:
            reply_text = f"消息太长，无法处理。{_text_length}"
        else:
            to_send_data = {"content": msgview.data_decoded}
    elif category == "PLAIN_IMAGE":
        try:
            _bytes, _ = get_filebytes(data)
            attachment_id = json.loads(_bytes).get("attachment_id")
            attachment = bot.xin.api.message.read_attachment(attachment_id)
            view_url = attachment["data"]["view_url"]
            content = requests.get(view_url).content
            to_send_data = {"images": [content]}
        except Exception as err:
            to_send_data = None
            reply_text = "Mixin 服务目前不稳定，请稍后再试，或联系开发者\n" + str(err)
            reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
            logger.warning(err)

    if to_send_data:
        pvtkey = bot.db.get_privatekey(msg_data.get("user_id"))
        try:
            resp = bot.rum.api.send_content(pvtkey, **to_send_data)
            if "trx_id" in resp:
                print(datetime.datetime.now(), resp["trx_id"], "sent_to_rum done.")
                reply_text = f"已成功生成 trx_id <{resp['trx_id']}>，加入上链队列"
            else:
                reply_text = f"发送到 RUM 种子网络时出错，请稍后再试，或联系开发者\n\n{resp}"
                reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
        except Exception as err:
            reply_text = f"发送到 RUM 种子网络时出错，请稍后再试，或联系开发者\n\n{err}"
            reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
            logger.warning(err)

    if reply_text:
        reply_msg = pack_message(
            pack_text_data(reply_text),
            conversation_id=msg_cid,
            quote_message_id=msg_id,
        )
        reply_msgs.insert(0, reply_msg)

    if reply_msgs:
        for msg in reply_msgs:
            resp = bot.xin.api.send_messages(msg)

    await bot.blaze.echo(msg_id)
    return


bot = BlazeBot()
bot.blaze = BlazeClient(
    bot.config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
    api_base=BLAZE_ZEROMESH,
)
bot.blaze.run_forever(2)
