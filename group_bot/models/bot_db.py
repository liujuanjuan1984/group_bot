import datetime
import json
import logging

from eth_account import Account
from eth_utils.hexadecimal import encode_hex

from group_bot.config import COMMON_ACCOUNT_PWD
from group_bot.models.base import BaseDB
from group_bot.models.keystore import KeyStore
from group_bot.models.profile import Profile
from group_bot.models.sent_msgs import SentMsgs
from group_bot.models.trx import Trx
from group_bot.models.trx_progress import TrxProgress

logger = logging.getLogger(__name__)


def _check_str_param(param):
    if param is None:
        return ""
    if isinstance(param, (dict, list)):
        return json.dumps(param)
    if not isinstance(param, str):
        try:
            return str(param)
        except:
            return ""
    return param


class BotDB(BaseDB):
    def get_all_rss_users(self):
        _mixin_ids = self.session.query(KeyStore.user_id).filter(KeyStore.is_rss != False).all()
        for _mixin_id in _mixin_ids:
            mid = _mixin_id[0]
            if mid != "00000000-0000-0000-0000-000000000000":
                yield mid

    def get_nicknames(self):
        _all_profiles = self.session.query(Profile).all()
        nicknames = {}
        for _profile in _all_profiles:
            nicknames[_profile.pubkey] = {"name": _profile.name}
        return nicknames

    def get_profile_by_pubkey(self, pubkey):
        return self.session.query(Profile).filter(Profile.pubkey == pubkey).first()

    def update_nickname(self, pubkey, name):
        if not name:
            name = pubkey[-10:-2]
        existd = self.get_profile_by_pubkey(pubkey)
        if existd:
            if existd.name != name:
                self.session.query(Profile).filter(Profile.pubkey == pubkey).update({"name": name})
                self.commit()
        else:
            self.add(Profile({"pubkey": pubkey, "name": name}))

    def get_keystore(self, mixin_id):
        return self.session.query(KeyStore).filter(KeyStore.user_id == mixin_id).first()

    def add_keystore(self, mixin_id, is_rss=True):
        account = Account().create()
        keystore = account.encrypt(COMMON_ACCOUNT_PWD)
        self.add(
            KeyStore(
                {
                    "user_id": mixin_id,
                    "keystore": json.dumps(keystore),
                    "is_rss": is_rss,
                }
            )
        )
        return keystore

    def update_rss(self, mixin_id, is_rss=True):
        existd = self.get_keystore(mixin_id)
        if existd:
            if existd.is_rss != is_rss:
                self.session.query(KeyStore).filter(KeyStore.user_id == mixin_id).update(
                    {"is_rss": is_rss}
                )
                self.commit()
        else:
            self.add_keystore(mixin_id, is_rss)

    def update_privatekey(self, mixin_id, private_key):
        try:
            account = Account().from_key(private_key)
            keystore = account.encrypt(COMMON_ACCOUNT_PWD)
            keystore = json.dumps(keystore)
        except:
            return
        existd = self.get_keystore(mixin_id)
        if existd:
            self.session.query(KeyStore).filter(KeyStore.user_id == mixin_id).update(
                {"keystore": keystore}
            )
            self.commit()
        else:
            self.add(
                KeyStore(
                    {
                        "user_id": mixin_id,
                        "keystore": keystore,
                        "is_rss": True,
                    }
                )
            )
        return keystore

    def get_privatekey(self, mixin_id: str) -> str:
        existd = self.get_keystore(mixin_id)
        if existd:
            keystore = json.loads(existd.keystore)
        else:
            keystore = self.add_keystore(mixin_id)

        pvtkey = Account().decrypt(keystore, COMMON_ACCOUNT_PWD)
        return encode_hex(pvtkey)

    def get_progress(self, progress_type):
        """get the trx_id of progress_type"""
        trx = (
            self.session.query(TrxProgress.trx_id)
            .filter(TrxProgress.progress_type == progress_type)
            .first()
        )
        if trx:
            return trx[0]

    def update_trx_progress(self, trx_id, timestamp, progress_type):
        if timestamp is None:
            timestamp = str(datetime.datetime.now())
        existd_trxid = self.get_progress(progress_type)
        if existd_trxid:
            if existd_trxid != trx_id:
                self.session.query(TrxProgress).filter(
                    TrxProgress.progress_type == progress_type
                ).update({"trx_id": trx_id, "timestamp": timestamp})
                self.commit()

        else:
            self.add(
                TrxProgress(
                    {
                        "progress_type": progress_type,
                        "trx_id": trx_id,
                        "timestamp": timestamp,
                    }
                )
            )

    def is_trx_existd(self, trx_id):
        if self.session.query(Trx).filter(Trx.trx_id == trx_id).first():
            return True
        return False

    def add_trx(self, trx_id, timestamp, text):
        self.add(
            Trx(
                {
                    "trx_id": trx_id,
                    "timestamp": timestamp,
                    "text": text,
                }
            )
        )

    def get_trxs_todo(self, timestamp):
        return (
            self.session.query(Trx)
            .filter(Trx.timestamp > timestamp)
            .filter(Trx.is_sent == False)
            .all()
        )

    def update_trx_as_sent(self, trx_id):
        self.session.query(Trx).filter(Trx.trx_id == trx_id).update({"is_sent": True})
        self.commit()

    def get_trx_by_message(self, message_id):
        trx = self.session.query(SentMsgs.trx_id).filter(SentMsgs.message_id == message_id).first()
        if trx:
            return trx[0]

    def add_sent_msg(self, message_id, trx_id, mixin_id):
        self.add(
            SentMsgs(
                {
                    "message_id": message_id,
                    "trx_id": trx_id,
                    "user_id": mixin_id,
                }
            )
        )
