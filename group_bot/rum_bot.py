import datetime
import logging

from mininode import MiniNode, utils
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import pack_message, pack_text_data

from group_bot.config import DB_NAME, HTTP_ZEROMESH, MINUTES, MIXIN_BOT_KEYSTORE, RUM_SEED_URL
from group_bot.models import BotDB

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
        p_tid = self.get_progress_and_check("GET_PROFILES")
        users_data = self.rum.api.get_profiles(
            users={"progress_tid": p_tid},
            types=("name",),
        )

        tid = users_data.get("progress_tid")
        self.db.update_trx_progress(tid, None, "GET_PROFILES")

        for pubkey in users_data:
            if pubkey == "progress_tid":
                continue
            self.db.update_nickname(pubkey, users_data[pubkey].get("name"))
        nicknames = self.db.get_nicknames()
        return nicknames

    def get_progress_and_check(self, progress_type):
        trx_id = None
        existd = self.db.get_trx_progress(progress_type)
        if existd:
            trx_id = existd.trx_id
            # check trx in the group chain.
            _trx = self.rum.api.get_trx(trx_id)
            if _trx.get("TrxId") != trx_id:
                trx_id = None
        return trx_id

    def get_group_trxs(self):
        nicknames = self.update_profiles()

        # get the trx_id and check it if exists in that group
        _ts = None
        trx_id = self.get_progress_and_check("GET_CONTENT")

        if trx_id is None:
            _trxs = self.rum.api.get_content(reverse=True, num=20)
            if len(_trxs) > 0:
                trx_id = _trxs[-1]["TrxId"]
                _ts = str(utils.timestamp_to_datetime(_trxs[-1]["TimeStamp"]))

        trxs = self.rum.api.get_content(start_trx=trx_id, num=20)
        for trx in trxs:
            # update progress of get group content
            _tid = trx["TrxId"]
            ts = str(utils.timestamp_to_datetime(trx["TimeStamp"]))
            self.db.update_trx_progress(_tid, ts, "GET_CONTENT")
            # add new trx to db
            if ts <= str(datetime.datetime.now() + datetime.timedelta(minutes=MINUTES)):
                continue
            if self.db.is_trx_existd(_tid):
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
            text = self._check_text(trx.text)
            packed = pack_text_data(text)
            for user_id in users:
                if self.db.is_trx_sent_to_user(trx.trx_id, user_id):
                    continue
                cid = self.xin.get_conversation_id_with_user(user_id)
                msg = pack_message(packed, cid)
                resp = self.xin.api.send_messages(msg)
                if "data" in resp:
                    self.db.add_trx_sent(trx.trx_id, user_id)
                    self.db.update_sent_msgs(resp["data"]["message_id"], trx.trx_id, user_id)
