import redis
import buu_config, buu_model
from buu_model import class_model

class class_database_op(object):

    def __init__(self):
        self.config = buu_config.config
        self.redis_ins = redis.Redis(host = self.config.redis_addr, port = self.config.redir_port,  \
                                    db = self.config.redis_db, password = self.config.redis_password)

    def flush_redis(self):
        self.redis_ins.flushdb()

    def put_user(self, userName):
        exist_userId = self.redis_ins.get('user-username-id-' + userName)
        if not exist_userId:
            exist_user = class_model.User(userName = userName)
            userId = exist_user.id
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return int(userId)
        else:
            return exist_userId

    def update_user(self, userName, userId):
        userId = int(userId)

        if self.redis_ins.get('user-id-username-' + str(userId)):
            if str(self.redis_ins.get('user-id-username-' + str(userId)).decode('utf-8')) == userName and \
                int(self.redis_ins.get('user-username-id-' + userName)) == userId:
                return None

        try:
            exist_user = class_model.User.select(class_model.User.q.id == userId).limit(1).getOne()
            exist_user.set(userName = userName)
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return None
        except Exception:
            exist_user = class_model.User(userName = userName)
            userId = exist_user.id
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return int(userId)

    def get_username_by_id(self, userId):
        userId = int(userId)
        exist_userName = self.redis_ins.get('user-id-username-' + str(userId))
        if exist_userName:
            return exist_userName.decode('utf-8')

        try:
            exist_user = class_model.User.select(class_model.User.q.id == int(userId)).limit(1).getOne()
            self.redis_ins.set('user-id-username-' + str(userId), exist_user.userName)
            self.redis_ins.set('user-username-id-' + exist_user.userName, userId)
            return exist_user.userName
        except Exception:
            return None

    def get_user_by_id(self, userId):
        try:
            exist_user = class_model.User.select(class_model.User.q.id == int(userId)).limit(1).getOne()
            return exist_user
        except Exception:
            return None


    def get_id_by_username(self, userName):
        exist_userId = self.redis_ins.get('user-username-id-' + userName)
        if exist_userId:
            return exist_userId

        try:
            exist_user = class_model.User.select(class_model.User.q.userName == userName).limit(1).getOne()
            userId = exist_user.id
            self.redis_ins.set('user-id-username-' + str(userId), userName)
            self.redis_ins.set('user-username-id-' + userName, userId)
            return userId
        except Exception:
            return None

    def get_user_current_step(self, userId):
        step = self.redis_ins.get('step-' + str(userId))
        if step:
            return step.decode('utf-8')

        return '0'

    def set_user_current_step(self, userId, step):
        self.redis_ins.set('step-' + str(userId), step)

    def step_back(self, userId):
        cur_step = self.get_user_current_step(userId)
        stop_pos = cur_step.rfind('-')
        if stop_pos != -1:
            cur_step = cur_step[:stop_pos]
        else:
            cur_step = '0'
        self.set_user_current_step(userId, cur_step)

    def set_redis_kv(self, userId, key, value):
        self.redis_ins.set('custom-' + str(userId) + '-' + str(key), value)

    def get_redis_kv(self, userId, key):
        return self.redis_ins.get('custom-' + str(userId) + '-' + str(key))

    def delete_redis_kv(self, userId, key):
        self.redis_ins.delete('custom-' + str(userId) + '-' + str(key))

    def save_card_info(self, userId, user_name, password):
        user_name = user_name.decode('utf-8')
        try:
            exist_card = class_model.Card.select(class_model.Card.q.user == self.get_user_by_id(userId)).limit(1).getOne()
            exist_card.set(user_name = user_name, password = password)
        except Exception:
            class_model.Card(user_name = user_name, password = password, user = self.get_user_by_id(userId))

    def get_card_info(self, userId):
        try:
            exist_card = class_model.Card.select(class_model.Card.q.user == self.get_user_by_id(userId)).limit(1).getOne()
            return exist_card
        except Exception:
            return None

    def get_function_info(self, userId, function_name):
        result = {}

        enable = self.redis_ins.get('function-' + str(userId) + '-' + function_name + '-enable')
        option = self.redis_ins.get('function-' + str(userId) + '-' + function_name + '-option')
        if enable is not None:
            result['enable'] = int(enable)
            result['option'] = option
            return result
        else:
            result['enable'] = 0
            result['option'] = ''

        try:
            function = class_model.Switch.select((class_model.Switch.q.user == self.get_user_by_id(userId)) & (class_model.Switch.q.function_name == function_name)).limit(1).getOne()
            result['enable'] = int(function.function_enable)
            result['option'] = function.function_option
            return result
        except Exception:
            return result

    def set_function_info(self, userId, function_name, enable, option):
        try:
            exist_function = class_model.Switch.select((class_model.Switch.q.user == self.get_user_by_id(userId)) & (class_model.Switch.q.function_name == function_name)).limit(1).getOne()
            exist_function.set(function_enable = enable, function_option = option)
            self.redis_ins.set('function-' + str(userId) + '-' + function_name + '-enable', int(enable))
            self.redis_ins.set('function-' + str(userId) + '-' + function_name + '-option', option)
        except Exception:
            class_model.Switch(function_enable = enable, function_option = option, function_name = function_name, user = self.get_user_by_id(userId))
            self.redis_ins.set('function-' + str(userId) + '-' + function_name + '-enable', int(enable))
            self.redis_ins.set('function-' + str(userId) + '-' + function_name + '-option', option)
