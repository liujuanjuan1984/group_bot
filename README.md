# Mixin Bot for Rum Group

这是一个基于 mixin messenger 的 bot 源码，让 mixin 的用户更方便地参与到 Rum 的生态之中。

## 概述

其功能是：

1、用户在 mixin messenger 上通过 bot 的聊天框发送文本或图片，bot 将自动为用户映射并托管密钥，并发布内容到指定的 rum 种子网络上。

可以在 config.py 中设定 USER_CAN_SEND_CONTENT 为 False 来关闭该功能，但用户依然可以通过回复来与内容互动。

特别地，

如果用户直接发送文本“修改昵称：新的昵称”（不包含引号）将修改用户在 rum 上所用密钥的昵称。

如果用户直接发送文本“更换密钥 0xxxxx”（不包含引号，密钥以0x开头，共66位，为 eth 兼容的私钥），可以更换身份为指定的密钥。特别留意，该方式仅仅为了方便用户重置身份，或统一自己在多个种子网络的身份，由此操作后，该密钥不再 100% 安全，该密钥不应该持有任何价值资产。

2、bot 从指定的 Rum 种子网络获取待转发的动态，推送给用户。

可以在 config.py 中设定 IS_LIKE_TRX_SENT_TO_USER 为 False 来关闭点赞类型的动态推送，但其它类型的动态依然会保持推送。

如果用户直接发送文本“取消订阅”（不包含引号），将不再收到动态推送；如果发送文本“订阅动态”，将重新收到动态推送。

用户在 mixin 上回复某条动态，也会自动在 rum 种子网络上产生相应的回复；

回复文本无长度限制；

如果回复文本在 `["赞", "点赞", "1", "+1"]` 之中，将在 rum 种子网络上生成为点赞；

回复文本在 `["踩", "点踩", "-1", "0"]` 之中，将生成为点踩。

3、bot 将记录用户的 mixin id ，并托管用户所映射的密钥，请注意，此处理决定了本 bot 不是完全去中心化或匿名的。

## 如何部署？

1、mixin bot： 在 mixin 开发者后台申请创建，获得 session keystore

2、rum seed：部署 Rum 种子网络；或者获取 Rum 种子网络的 seed，需符合轻节点访问要求（host:port?=jwt 等参数满足轻节点远程访问）

3、拷贝源码，初始化环境

```bash
git clone https://github.com/liujuanjuan1984/group_bot.git
cd group_bot
```

初始化环境：

```pip install -r requirements.txt```

4、更新配置文件，初始化 db

- group_bot/config.py
- group_bot/config_private.py


```bash
python do_db_init.py
```

5、启动并持续运行如下服务：

- blaze 服务：监听 mixin user 发给 mixin bot 的消息，并把内容发送到指定的 rum 种子网络

```bash
python do_blaze.py
```

- rss 服务：从 rum 获取最新内容，并生成动态，在 mixin 上推送给 user

```bash
python do_rum_to_xin.py
```

## 依赖：

- Mixin [mixinsdk](https://pypi.org/project/mixinsdk/)
- QuoRum [mininode](https://github.com/liujuanjuan1984/mininode)

## 代码格式化

Install:

```bash
pip install black
pip install isort
```

Format:

```bash
isort .
black -l 100 -t py39 .
pylint group_bot > pylint.check_rlt.log
```
