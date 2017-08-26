import itchat

import buu_config
import buu_msg_handle
import buu_database
import sys
import buu_model
import buu_thread_read_remark
import buu_thread_card

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    return msg_handler.msg_handle(msg)

@itchat.msg_register(itchat.content.FRIENDS)
def add_friend(msg):
    itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    itchat.send_msg(welcome_msg, msg['RecommendInfo']['UserName'])


buu_model.class_model.init()

msg_handler = buu_msg_handle.class_msg_handle()

itchat.auto_login(enableCmdQR=2, hotReload=True)

class_database_op = buu_database.class_database_op()
class_database_op.flush_redis()

buu_thread_read_remark.class_init_thread()
buu_thread_card.class_init_thread()

itchat.run()
