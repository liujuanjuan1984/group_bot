# the treehole bot's keystore file, init from dashboard of mixin.
MIXIN_BOT_KEYSTORE = {
    "pin": "123474",
    "client_id": "30789e31-xxxx-xxxx-xxxx-1a45e781ae2e",
    "session_id": "d92a35ea-xxxx-xxxx-xxxx-3ccb3491e013",
    "pin_token": "q0ij-E04eCWXpq3SXzp2UXnaitt3JMwPlh1a9NsCQ3M",
    "private_key": "nxw2h201ESDA2_ReiExxxxxt06qj5i2Men_SIUP2IZiwgGe0g8pAsItelRNNNgvjyIKYg0eWvtecH9essI-xqg",
}

# update the mixin_id of developer
DEV_MIXIN_ID = "30789e31-xxxx-xxxx-xxxx-1a45e781ae2e"

# the password to init keystore from private key
COMMON_ACCOUNT_PWD = "your-password"

USER_CAN_SEND_CONTENT = True
IS_LIKE_TRX_SENT_TO_USER = False 

# the rum group's seed url, init by fullnode joined or created the group.
# send content to this rum group
RUM_SEED_URL = f"rum://seed?v=1&e=0&n=0&b=i7pFz0vLTxCwuNUkcrgryg&c=PSkLJ6i_j9vj3QXKBm_bIv587GvtT97VnLMjEExFHeg&g=pPpuGjVLT3Os6tdxI-J7dQ&k=Ask-2-gEfTkCYjLBYd1WIlQ3PI0-Lh-9hvb4X-h0ZU9C&s=5B8QmNCdt-Pty9glyvZkzHtW7CjK61doDN2PAFppFyAOZyFXbH1zGO8jHkBYCSnpafCg7EHy4x8EZB2XWiOseQE&t=Fw48p9yON1Q&a=treehole_from_mixin_pic&y=group_timeline&u=http%3A%2F%2F127.0.0.1%3A57772%3Fjwt%3DeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGxvd0dyb3VwcyI6WyJhNGZhNmUxYS0zNTRiLTRmNzMtYWNlYS1kNzcxMjNlMjdiNzUiXSwiZXhwIjoxODE5MDEyMDA1LCJuYW1lIjoiYWxsb3ctYTRmYTZlMWEtMzU0Yi00ZjczLWFjZWEtZDc3MTIzZTI3Yjc1Iiwicm9sZSI6Im5vZGUifQ.DjlDCIwwMIAoERjaV-H34aZkeyn4AgSL4fNcKWSMvSM"

# the pttn and repl for re.sub to replace the text in the message.
RE_PAIRS = [
  ( r"""<a href="(https://sample.com/.*?)" class=".*?">查看全文</a>""",r'查看全文 \1'),
]
