import datetime
import json
import logging

from eth_account import Account
from eth_utils.hexadecimal import encode_hex

from group_bot.config import COMMON_ACCOUNT_PWD, MIXIN_BOT_KEYSTORE
from group_bot.models import Base
from group_bot.models.base import BaseDB
from group_bot.models.keystore import KeyStore
from group_bot.models.profile import Profile
from group_bot.models.sent_msgs import SentMsgs
from group_bot.models.trx import Trx
from group_bot.models.trx_progress import TrxProgress
from group_bot.models.trx_status import TrxStatus

logger = logging.getLogger(__name__)


def _check_str_param(param):
    if param is None:
        return ""
    elif type(param) in [dict, list]:
        return json.dumps(param)
    elif type(param) != str:
        try:
            return str(param)
        except:
            return ""
    return param


class BotDB(BaseDB):
    def get_all_users(self):
        _mixin_ids = self.session.query(KeyStore.user_id).all()
        return [_mixin_id[0] for _mixin_id in _mixin_ids]

    def get_key(self, mixin_id):
        return self.session.query(KeyStore).filter(KeyStore.user_id == mixin_id).first()

    def add_key(self, mixin_id):
        account = Account.create()
        keystore = account.encrypt(COMMON_ACCOUNT_PWD)
        _k = {
            "user_id": mixin_id,
            "keystore": json.dumps(keystore),
        }
        self.add(KeyStore(_k))
        return keystore

    def get_privatekey(self, mixin_id: str) -> str:
        key = self.get_key(mixin_id)
        if key:
            keystore = json.loads(key.keystore)
        else:
            keystore = self.add_key(mixin_id)

        pvtkey = Account.decrypt(keystore, COMMON_ACCOUNT_PWD)
        return encode_hex(pvtkey)

    def get_trx_progress(self, progress_type):
        return self.session.query(TrxProgress).filter(TrxProgress.progress_type == progress_type).first()

    def add_trx_progress(self, trx_id, timestamp, progress_type):
        _p = {
            "progress_type": progress_type,
            "trx_id": trx_id,
            "timestamp": timestamp,
        }
        self.add(TrxProgress(_p))

    def update_trx_progress(self, trx_id, timestamp, progress_type):
        if self.get_trx_progress(progress_type):
            self.session.query(TrxProgress).filter(TrxProgress.progress_type == progress_type).update(
                {"trx_id": trx_id, "timestamp": timestamp}
            )
            self.commit()

        else:
            self.add_trx_progress(trx_id, timestamp, progress_type)

    def get_trx(self, trx_id):
        return self.session.query(Trx).filter(Trx.trx_id == trx_id).first()

    def add_trx(self, trx_id, timestamp, text):

        _p = {
            "trx_id": trx_id,
            "timestamp": timestamp,
            "text": text,
        }

        self.add(Trx(_p))

    def get_trxs_later(self, timestamp):
        return self.session.query(Trx).filter(Trx.timestamp > timestamp).all()

    def get_users_by_trx_sent(self, trx_id):
        _sent_users = self.session.query(TrxStatus.user_id).filter(TrxStatus.trx_id == trx_id).all()
        return [_sent_user[0] for _sent_user in _sent_users]

    def add_trx_sent(self, trx_id, user_id):

        _p = {
            "trx_id": trx_id,
            "user_id": user_id,
        }
        self.add(TrxStatus(_p))

    def get_sent_msg(self, message_id):
        return self.session.query(SentMsgs).filter(SentMsgs.message_id == message_id).first()

    def update_sent_msgs(self, message_id, trx_id, mixin_id):
        if self.get_sent_msg(message_id):
            return

        _p = {
            "message_id": message_id,
            "trx_id": trx_id,
            "user_id": mixin_id,
        }
        self.add(SentMsgs(_p))
