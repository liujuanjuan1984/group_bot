# Mixin Bot for Rum Group

这是一个基于 mixin messenger 的 bot 源码，让 mixin 的用户更方便地参与到 Rum 的生态之中。

其功能是：

1、用户在 mixin messenger 上通过 bot 的聊天框发送文本或图片，bot 将自动为用户映射并托管密钥，并发布内容到指定的 Rum 种子网络 上

2、bot 从指定的 Rum 种子网络获取待转发的动态，推送给用户

3、bot 将记录用户的 mixin id ，并托管用户所映射的密钥，请注意，这并不是完全去中心化或匿名的

## 如何部署？

1、mixin bot： 在 mixin 开发者后台申请创建，获得 session keystore

2、rum seed：部署 Rum 种子网络；或者获取 Rum 种子网络的 seed，需符合轻节点访问要求（host:port?=jwt 等参数满足轻节点远程访问）

3、拷贝源码，初始化环境

```bash
git clone https://github.com/liujuanjuan1984/mixin_bot_for_rum_group.git
cd mixin_bot_for_rum_group
```

初始化环境：

```pip install -r requirements.txt```

4、更新配置文件

- rss/config.py
- rss/config_private.py 

5、启动如下服务：

- blaze 服务：监听 user 发给 mixin bot 的消息，并写入消息 db

```bash
python do_blaze.py
```

- rss 服务：从 rum 获取最新内容，并推送给用户

```bash
python do_get_trxs.py
python do_rum_to_xin.py
```

- rum 服务：把内容发送到指定的 rum 种子网络

```bash
python do_xin_to_rum.py
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
black -l 120 -t py39 .
```
