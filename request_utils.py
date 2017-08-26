import requests
import re
import buu_config, buu_database
import utils

class request_utils(object):
    def __init__(self):
        self.config = buu_config.config
        self.session = requests.Session()
        self.has_login_vpn = False
        self.has_login_mybuu = False
        self.has_login_card = False
        self.class_database_op = buu_database.class_database_op()

    def webvpn_login(self):
        r = self.session.get('https://webvpn.buu.edu.cn/users/sign_in')
        csrf_token = re.compile('<meta name="csrf-token" content="(.*)" />').findall(r.text)[0]

        payload = {'utf8': '✓', 'authenticity_token': csrf_token, \
                    'user[login]': self.config.mybuu_username, 'user[password]': self.config.mybuu_password, \
                    'commit': '登            录'}
        r = self.session.post("https://webvpn.buu.edu.cn/users/sign_in", data = payload)

        try:
            re.compile('<li><a rel="nofollow" data-method="delete" href="/users/sign_out">(.*)</a></li>').findall(r.text)[0]
            return True
        except Exception:
            return False

    def get_real_domain(self, domain_prefix, suffix = ""):
        if self.config.need_vpn:
            if utils.is_ip(domain_prefix):
                domain_prefix = domain_prefix.replace('.', '-')
            return "https://" + domain_prefix + ".webvpn.buu.edu.cn" + suffix
        else:
            if utils.is_ip(domain_prefix):
                return "http://" + domain_prefix + suffix
            else:
                return "http://" + domain_prefix + ".buu.edu.cn" + suffix

    def get_real_domain_encoded(self, domain_prefix, suffix = ""):
        import urllib
        if self.config.need_vpn:
            if utils.is_ip(domain_prefix):
                domain_prefix = domain_prefix.replace('.', '-')
            return urllib.parse.quote_plus("https://" + domain_prefix + ".webvpn.buu.edu.cn" + suffix)
        else:
            if utils.is_ip(domain_prefix):
                return urllib.parse.quote_plus("http://" + domain_prefix + suffix)
            else:
                return urllib.parse.quote_plus("http://" + domain_prefix + ".buu.edu.cn" + suffix)

    def mybuu_login(self, userId):
        if self.config.need_vpn and not self.has_login_vpn:
            if not self.webvpn_login():
                return

        r = self.session.get(self.get_real_domain("ids") + "/authserver/login?service=https%3A%2F%2Fmy.webvpn.buu.edu.cn%2F")

        card = self.class_database_op.get_card_info(userId)
        if card:
            lt = re.compile('<input type="hidden" name="lt" value="(.*)" />').findall(r.text)[0]

            payload = {'username': card.user_name, 'password': card.password, \
                        'lt': lt, 'execution': 'e1s1', \
                        '_eventId': 'submit', 'rmShown': 1}
            r = self.session.post(self.get_real_domain("ids") + "/authserver/login?service=http%3A%2F%2Fmy.webvpn.buu.edu.cn%2F", data = payload)
            self.has_login_mybuu = True
            return True
        else:
            return False

    def card_login(self, userId):
        if not self.has_login_mybuu:
            self.mybuu_login(userId)

        self.session.get(self.get_real_domain("ids") + "/authserver/login?service=" + self.get_real_domain_encoded("10.11.10.13", "/lhdxPortalHome.action"))
        self.has_login_card = True

    def card_balance_check(self, userId):
        if not self.has_login_card:
            self.card_login(userId)

        # https://10-11-10-13.webvpn.buu.edu.cn/pages/card/cardMain.jsp
        # https://10-11-10-13.webvpn.buu.edu.cn/accountcardUser.action
        # payload = {'imageField.x': 30, 'imageField.y': 12}
        # r = self.session.post(self.get_real_domain("10.11.10.13") + "/pages/card/cardMain.jsp", data = payload)

        r = self.session.get(self.get_real_domain("10.11.10.13") + "/accountcardUser.action")

        try:
            balance = {}
            # <td class="neiwen">67.60元（卡余额）0.00元(当前过渡余额)0.00元(上次过渡余额)</td>
            balance['current'] = round(float(re.compile(r"<td class=\"neiwen\">(.*)\u5143\uff08\u5361\u4f59\u989d\uff09").findall(r.text)[0]), 2)
            balance['current_pending'] = round(float(re.compile(r"\u5143\uff08\u5361\u4f59\u989d\uff09(.*)\u5143\u0028\u5f53\u524d\u8fc7\u6e21\u4f59\u989d\u0029").findall(r.text)[0]), 2)
            balance['pre_pending'] = round(float(re.compile(r"\u5143\u0028\u5f53\u524d\u8fc7\u6e21\u4f59\u989d\u0029(.*)\u5143\u0028\u4e0a\u6b21\u8fc7\u6e21\u4f59\u989d\u0029").findall(r.text)[0]), 2)
            return balance
        except Exception:
            import traceback
            traceback.print_exc()
            return None

    def card_get_today_total(self, userId):
        if not self.has_login_card:
            self.card_login(userId)

        r = self.session.get(self.get_real_domain("10.11.10.13") + "/accountcardUser.action")

        user_account_id = re.compile(r"<div align=\"left\">(.*)</div>").findall(r.text)[1]

        payload = {'account': user_account_id, 'inputObject': 'all', \
                    'Submit': ' 确 定 '}

        r = self.session.post(self.get_real_domain("10.11.10.13") + "/accounttodatTrjnObject.action", data = payload)

        today_total = round(float(re.compile(r"\u603b\u4ea4\u6613\u989d\u4e3a\u003a(.*)\uff08\u5143\uff09").findall(r.text)[0]), 2)
        return today_total

    def card_get_history_log(self, userId, begindate, enddate):
        if not self.has_login_card:
            self.card_login(userId)

        r = self.session.get(self.get_real_domain("10.11.10.13") + "/accountcardUser.action")

        user_account_id = re.compile(r"<div align=\"left\">(.*)</div>").findall(r.text)[1]

        payload = {'account': user_account_id, 'inputObject': 'all', \
                    'Submit': ' 确 定 '}

        r = self.session.post(self.get_real_domain("10.11.10.13") + "/accounthisTrjn.action", data = payload)

        next_url = re.compile(r"action=\"(.*)\" method=\"post").findall(r.text)[0]

        payload = {'account': user_account_id, 'inputObject': 'all', \
                    'Submit': ' 确 定 '}

        r = self.session.post(self.get_real_domain("10.11.10.13") + next_url, data = payload)

        next_url = re.compile(r"action=\"(.*)\" method=\"post").findall(r.text)[0]

        payload = {'inputStartDate': begindate, 'inputEndDate': enddate}

        r = self.session.post(self.get_real_domain("10.11.10.13") + next_url, data = payload)

        next_url = re.compile(r"action=\"(.*)\" method=\"post").findall(r.text)[0]

        r = self.session.post(self.get_real_domain("10.11.10.13") + "/accounthisTrjn.action" + next_url)

        pagenum = int(re.compile(r"\u5171(.*)\u9875\u0026\u006e\u0062\u0073\u0070\u003b\u0026\u006e\u0062\u0073\u0070\u003b\u5f53\u524d\u7b2c").findall(r.text)[0])

        ret_list = []
        try:
            for current_page in range(1, pagenum + 1):
                payload = {'inputStartDate': begindate, 'inputEndDate': enddate, 'pageNum': current_page}
                r = self.session.post(self.get_real_domain("10.11.10.13") + "/accountconsubBrows.action", data = payload)
                temp_list = re.compile(r"<tr class=\"listbg", flags = re.DOTALL).findall(r.text)

                key_list = re.compile(r"<td(.*)align=\"(center|right)\"( |)>(\S*|(\S*\s\S*))(\s*|)</td>", flags = re.M).findall(r.text)

                key_list = key_list[5:]

                item_len = len(temp_list)

                for i in range(0, item_len):
                    single_item = {}
                    single_item['time'] = key_list[i * 9][3]
                    single_item['user_name'] = key_list[i * 9 + 1][3]
                    single_item['user_real_name'] = key_list[i * 9 + 2][3]
                    single_item['type'] = key_list[i * 9 + 3][3]
                    single_item['sub_system_name'] = key_list[i * 9 + 4][3]
                    single_item['amount'] = float(key_list[i * 9 + 5][3])
                    single_item['current_balance'] = float(key_list[i * 9 + 6][3])
                    single_item['count'] = int(key_list[i * 9 + 7][3])
                    single_item['status'] = key_list[i * 9 + 8][3]
                    ret_list.append(single_item)
            return ret_list
        except Exception:
            import traceback
            traceback.print_exc()
            return None

    def card_get_total_consume(self, userId, begindate, enddate):
        if not self.has_login_card:
            self.card_login(userId)

        r = self.session.get(self.get_real_domain("10.11.10.13") + "/accountcardUser.action")

        user_account_id = re.compile(r"<div align=\"left\">(.*)</div>").findall(r.text)[1]

        payload = {'account': user_account_id, 'inputObject': 'all', \
                    'Submit': ' 确 定 '}

        r = self.session.post(self.get_real_domain("10.11.10.13") + "/accounthisTrjn.action", data = payload)

        next_url = re.compile(r"action=\"(.*)\" method=\"post").findall(r.text)[0]

        payload = {'account': user_account_id, 'inputObject': 'all', \
                    'Submit': ' 确 定 '}

        r = self.session.post(self.get_real_domain("10.11.10.13") + next_url, data = payload)

        next_url = re.compile(r"action=\"(.*)\" method=\"post").findall(r.text)[0]

        payload = {'inputStartDate': begindate, 'inputEndDate': enddate}

        r = self.session.post(self.get_real_domain("10.11.10.13") + next_url, data = payload)

        next_url = re.compile(r"action=\"(.*)\" method=\"post").findall(r.text)[0]

        r = self.session.post(self.get_real_domain("10.11.10.13") + "/accounthisTrjn.action" + next_url)

        consume_amount = float(re.compile(r"\u603b\u8ba1\u4ea4\u6613\u989d\u4e3a\u003a(.*)\uff08\u5143\uff09").findall(r.text)[0])

        return consume_amount
