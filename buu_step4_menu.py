import buu_database
import buu_config
import utils

class class_step(object):

    def __init__(self):
        self.step_dict = [  \
                            (None, None), \
                            (self.list_admin, None), \
                            (self.who_am_i, None), \
                            (self.sys_info, None), \
                            (self.about, None) \
                        ]
        self.config = buu_config.config
        self.class_database_op = buu_database.class_database_op()

    def list_admin(self, msg, userId):
        self.class_database_op.step_back(userId)
        return "管理员ID:" + str(self.config.admin_id)

    def who_am_i(self, msg, userId):
        self.class_database_op.step_back(userId)
        if userId == self.config.admin_id:
            return "管理员" + msg['FromUserName']
        else:
            return "普通用户" + msg['FromUserName']

    def sys_info(self, msg, userId):
        self.class_database_op.step_back(userId)
        loadavg = utils.load_stat()
        mem = utils.memory_stat()
        uptime = utils.uptime_stat()
        uptime_str = "Day %s, Hour %s, Minute %s, Second %s" % (uptime['day'], uptime['hour'], uptime['minute'], uptime['second'])
        return "系统负载：%s/%s/%s\n系统内存：%s/%s MB\n系统运行时间：%s" % \
                (loadavg['lavg_1'], loadavg['lavg_5'], loadavg['lavg_15'], \
                mem['MemUsed'], mem['MemTotal'], uptime_str
                )

    def about(self, msg, userId):
        self.class_database_op.step_back(userId)
        return 'Powered by secti6n @ BUU \nMade with Love \n最后更新时间：%s'%(self.config.version)

    def step_tips(self, msg, userId):
        return  '1 - 列出管理员\n' \
                '2 - 我是谁\n' \
                '3 - 系统信息\n' \
                '4 - 关于\n' \
                '5 - 洗衣机概率测算\n' \
                '其他输入 - 返回首页'
