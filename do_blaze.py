import datetime
import json
import logging
import re

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

    if action == "ERROR":
        logger.warning(message["error"])

    if action != "CREATE_MESSAGE":
        return

    error = message.get("error")
    if error:
        logger.warning(str(error))
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
    is_echo = True
    to_send_data = {}
    reply_text = ""
    reply_msgs = []
    mixin_id = msg_data.get("user_id")
    pvtkey = bot.db.get_privatekey(mixin_id)
    quote_message_id = msg_data.get("quote_message_id")

    if category not in ["PLAIN_TEXT", "PLAIN_IMAGE"]:
        err = f"暂不支持此类消息，category: {category}\n{msg_data}"
        logger.warning(err)
    elif category == "PLAIN_TEXT":
        text = MessageView.from_dict(msg_data).data_decoded
        to_send_data["content"] = text
        _text_length = f"文本长度需在 {TEXT_LENGTH_MIN} 至 {TEXT_LENGTH_MAX} 之间"
        if not quote_message_id:
            if text.lower() in ["hi", "hello", "nihao", "你好", "help", "?", "？"]:
                reply_text = WELCOME_TEXT
                to_send_data = {}
            elif text.startswith("修改昵称") and len(text) <= 5:
                reply_text = f"昵称太短，无法处理。"
                to_send_data = {}
            elif text.startswith("更换密钥") and len(text) <= 75 and len(text) >= 66:
                try:
                    _pvtkey = re.findall(r"[a-fA-F0-9]{64,66}", text)[0]
                    if not _pvtkey.startswith("0x") and len(_pvtkey) == 64:
                        _pvtkey = "0x" + _pvtkey
                    k = bot.db.update_privatekey(mixin_id, _pvtkey)
                    if k:
                        reply_text = f"密钥已更换，请注意该方式并非 100% 安全，请勿采用该密钥持有大额资产"
                    else:
                        reply_text = "密钥更换失败，请提供正确的密钥，共 66 位字符，以 0x 开头"
                except Exception as err:
                    reply_text = f"密钥更换失败，{err}"
                to_send_data = {}
            elif len(text) <= TEXT_LENGTH_MIN:
                reply_text = f"消息太短，无法处理。{_text_length}"
                to_send_data = {}
            elif len(text) >= TEXT_LENGTH_MAX:
                reply_text = f"消息太长，无法处理。{_text_length}"
                to_send_data = {}
    elif category == "PLAIN_IMAGE":
        try:
            _bytes, _ = get_filebytes(data)
            attachment_id = json.loads(_bytes).get("attachment_id")
            attachment = bot.xin.api.message.read_attachment(attachment_id)
            view_url = attachment["data"]["view_url"]
            content = requests.get(view_url).content
            to_send_data["images"] = [content]
        except Exception as err:
            to_send_data = {}
            reply_text = "Mixin 服务目前不稳定，将自动为您继续尝试\n" + str(err)
            logger.warning(err)
            is_echo = False

    if to_send_data:
        resp = None
        quoted = None
        text = to_send_data.get("content", "")

        if quote_message_id:
            quoted = bot.db.get_sent_msg(quote_message_id)
        if quoted:
            if text in ["赞", "点赞", "1", "+1"]:
                resp = bot.rum.api.like(pvtkey, quoted.trx_id)
            elif text in ["踩", "点踩", "-1", "0"]:
                resp = bot.rum.api.like(pvtkey, quoted.trx_id, "Dislike")
            else:
                resp = bot.rum.api.reply_trx(pvtkey, trx_id=quoted.trx_id, **to_send_data)
        else:
            if text.startswith("修改昵称:") or text.startswith("修改昵称："):
                name = text[5:] or "昵称太短请重新修改"
                name = name.replace(" ", "_").replace("\n", "-")
                resp = bot.rum.api.update_profile(pvtkey, name=name)
            else:
                resp = bot.rum.api.send_content(pvtkey, **to_send_data)

        if resp and "trx_id" in resp:
            print(datetime.datetime.now(), resp["trx_id"], "sent_to_rum done.")
            reply_text = f"已生成 trx {resp['trx_id']}，排队上链中..."
            bot.db.update_sent_msgs(msg_id, resp["trx_id"], mixin_id)
        else:
            reply_text = f"发送到 RUM 时出错，将自动为您继续尝试\n{resp}"
            reply_msgs.append(pack_message(pack_contact_data(DEV_MIXIN_ID), msg_cid))
            logger.warning(reply_text)
            is_echo = False

    if reply_text:
        reply_msg = pack_message(
            pack_text_data(reply_text),
            conversation_id=msg_cid,
            quote_message_id=msg_id,
        )
        reply_msgs.insert(0, reply_msg)

    for msg in reply_msgs:
        bot.xin.api.send_messages(msg)
    if is_echo:
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
