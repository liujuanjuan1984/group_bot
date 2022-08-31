import datetime
import logging
import re
import time

from mininode import MiniNode, utils
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import pack_message, pack_text_data

from group_bot.config import *
from group_bot.models import BotDB, KeyStore, Profile, Trx, TrxProgress

logger = logging.getLogger(__name__)


class RumBot:
    def __init__(
        self,
        db_name=DB_NAME,
        mixin_keystore=MIXIN_BOT_KEYSTORE,
        seedurl=RUM_SEED_URL,
    ):
        self.config = AppConfig.from_payload(mixin_keystore)
        self.db = BotDB(db_name, echo=False, reset=False)
        self.xin = HttpClient_AppAuth(self.config, api_base=HTTP_ZEROMESH)
        self.rum = MiniNode(seedurl)

    def update_profiles(self):
        progress = self.db.session.query(TrxProgress).filter(TrxProgress.progress_type == "GET_PROFILES").first()
        if progress is None:
            _p = {
                "progress_type": "GET_PROFILES",
                "trx_id": None,
                "timestamp": None,
            }
            self.db.add(TrxProgress(_p))
            p_tid = None
        else:
            p_tid = progress.trx_id

        try:
            users_data = self.rum.api.get_profiles(
                users={"progress_tid": p_tid},
                types=("name",),
            )
        except Exception as e:
            logger.warning(f"update_profiles error:{e}")
            return
        if users_data is None:
            return
        tid = users_data.get("progress_tid")

        if tid and tid != p_tid:
            self.db.session.query(TrxProgress).filter(TrxProgress.progress_type == "GET_PROFILES").update(
                {"trx_id": tid}
            )
            self.db.session.commit()

        for pubkey in users_data:
            if pubkey == "progress_tid":
                continue
            _name = users_data[pubkey].get("name", pubkey)
            existd = self.db.session.query(Profile).filter(Profile.pubkey == pubkey).first()
            if not existd:
                _p = {"pubkey": pubkey, "name": _name}
                self.db.add(Profile(_p))

            elif _name != existd.name:
                self.db.session.query(Profile).filter(Profile.pubkey == pubkey).update({"name": _name})
                self.db.commit()

    def get_nicknames(self):
        _all_profiles = self.db.session.query(Profile).all()
        nicknames = {}
        for _profile in _all_profiles:
            nicknames[_profile.pubkey] = {"name": _profile.name}
        return nicknames

    def get_group_trxs(self):
        self.update_profiles()
        nicknames = self.get_nicknames()

        # 获取 group trx 的更新进度
        existd = self.db.get_trx_progress("GET_CONTENT")
        if existd:
            trx_id = existd.trx_id
        else:
            _trxs = self.rum.api.get_content(reverse=True, num=20)
            if len(_trxs) > 0:
                trx_id = _trxs[-1]["TrxId"]
                _ts = str(utils.timestamp_to_datetime(_trxs[-1]["TimeStamp"]))
            else:
                trx_id = None
                _ts = None

            self.db.add_trx_progress(trx_id, _ts, "GET_CONTENT")

        trxs = self.rum.api.get_content(start_trx=trx_id, num=20)
        for trx in trxs:
            # update progress of get group content
            _tid = trx["TrxId"]
            ts = str(utils.timestamp_to_datetime(trx["TimeStamp"]))
            self.db.update_trx_progress(_tid, ts, "GET_CONTENT")
            # add new trx to db
            if ts <= str(datetime.datetime.now() + datetime.timedelta(minutes=MINUTES)):
                continue
            if self.db.get_trx(_tid):
                continue

            obj = self.rum.api.trx_retweet_params(trx, nicknames)
            if not obj:
                continue
            text = obj["content"].encode().decode("utf-8")
            self.db.add_trx(_tid, ts, text)

    def _check_text(self, text):
        _length = 200
        if len(text) > _length:
            text = text[:_length] + "...略..."
        return text

    def send_group_msg_to_xin(self):
        nice_ts = str(datetime.datetime.now() + datetime.timedelta(minutes=MINUTES))
        trxs = self.db.get_trxs_later(nice_ts)
        users = self.db.get_all_users()

        for trx in trxs:
            sent_users = self.db.get_users_by_trx_sent(trx.trx_id)
            text = self._check_text(trx.text)
            packed = pack_text_data(text)
            for user_id in users:
                if user_id in sent_users:
                    continue
                cid = self.xin.get_conversation_id_with_user(user_id)
                msg = pack_message(packed, cid)
                resp = self.xin.api.send_messages(msg)

                if "data" in resp:
                    self.db.add_trx_sent(trx.trx_id, user_id)
                    self.db.update_sent_msgs(resp["data"]["message_id"], trx.trx_id, user_id)

    def send_to_rum(self):
        quote_msgs = self.db.get_messages_to_send_with_quote()
        for msg in quote_msgs:
            quoted = self.db.get_sent_msg(msg.quote_message_id)
            if quoted:
                pvtkey = self.db.get_privatekey(msg.user_id)
                if msg.text in ["赞", "点赞", "1", "+1"]:
                    resp = self.rum.api.like(pvtkey, quoted.trx_id)
                elif msg.text in ["踩", "点踩", "-1", "0"]:
                    resp = self.rum.api.like(pvtkey, quoted.trx_id, "Dislike")
                else:
                    resp = self.rum.api.reply_trx(
                        pvtkey,
                        quoted.trx_id,
                        content=msg.text,
                    )
                if "trx_id" in resp:
                    logger.debug(datetime.datetime.now(), "send_to_rum, message_id:", msg.message_id)
                    self.db.set_message_sent(msg.message_id)
                    self.db.update_sent_msgs(msg.message_id, resp["trx_id"], msg.user_id)

        mixin_msgs = self.db.get_messages_to_send()
        for msg in mixin_msgs:
            if len(msg.text) < 5:  # too short to send
                continue

            pvtkey = self.db.get_privatekey(msg.user_id)
            resp = self.rum.api.send_content(pvtkey, content=msg.text)

            if "trx_id" in resp:
                logger.debug(datetime.datetime.now(), "send_to_rum, message_id:", msg.message_id)
                self.db.set_message_sent(msg.message_id)
                self.db.update_sent_msgs(msg.message_id, resp["trx_id"], msg.user_id)
