# @Time    : 18-9-12 上午10:40
# @Author  : Chao
# @File    : wechat.py
import requests
import json
from utils.log import logger


class Wechat_Client:
    def __init__(self):
        self.token = self.get_token('ww55d9b3690ed9a769', '0XJwa8pj-qwaxPqfvfZ9tenVO2jH85GRZ4RCO6f-sZw')

    def get_token(self,corpid, secrete):
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (corpid, secrete)
        resp = requests.get(url)
        data = json.loads(resp.content)
        logger.info('获取token结果: ' + json.dumps(data))
        if data['errcode'] == 0:
            return data['access_token']
        else:
            return None


    def get_department_list(self, token):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/department/list?access_token=%s&id=' % token
        resp = requests.get(url)
        data = json.loads(resp.content)
        logger.info('获取部门信息:' + json.dumps(data))
        if data['errcode'] == 0:
            return data['department']
        else:
            return []

    def build_tree(self, departments):
        """
        :param departments: 企业微信返回的部门列表
        :return:
            {
                1: {
                    'info': {'id': 1, 'name': '黄超的公司', 'parentid': 0, 'order': 100000000},
                    'children': [1, 2, 3]
                },
                ...
            }
        """
        id_map = {1: {'info': departments[0], 'children': []}}
        for dep in departments[1:]:
            id_map[dep['id']] = {
                'info': dep,
                'children': []
            }

            id_map[dep['parentid']]['children'].append(dep['id'])
        return id_map

    def get_dn(self, dep_tree, depid):
        """
        根据部门id来生成组的dn
        :param dep_tree: 公司的组织架构， 详见build_tree
        :param depid: 部门id
        :return:
        """
        dn = []
        tmp = depid
        while depid in dep_tree:
            dn.insert(0, dep_tree[depid]['info']['name'])
            depid = dep_tree[depid]['info']['parentid']
        logger.info('获取dn信息-- depid: %d; dn: %s' % (tmp, json.dumps(dn)))
        return "cn=" + '-'.join(dn) + ",ou=GROUPS,ou=people,dc=huangchao,dc=com"

    def get_users(self, depid, token, recursive=0):
        """
        获取某个部门的所有员工信息
        :param recursive: 是否获取子部门的员工信息
        :param depid: 部门id
        :param token: 认真token
        :return:
        """
        url = 'https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=%s&department_id=%s&fetch_child=%d' % (token, str(depid), recursive)
        resp = requests.get(url)
        data = json.loads(resp.content)
        logger.info('部门员工信息: ' + json.dumps(data))
        if data['errcode'] == 0:
            return data['userlist']
        else:
            logger.error('获取部门员工失败' + json.dumps(data))
            return []

if __name__ == "__main__":
    # token = get_token('ww55d9b3690ed9a769', '0XJwa8pj-qwaxPqfvfZ9tenVO2jH85GRZ4RCO6f-sZw')
    # token = "NLd-eJ1-7c0Gvvq3S_r6aMjfKJOld1HN8uEHR4Mbf47NvqjVY29haTJBI2bzxKC7oUO44jLUjwyXKrG3QmIbKF6ixh8D9eFlYOgGTKVl9Jg1YbfH7YjzkafQuQ71R3-qw4FDsw_k9QPF_65Q3sn_la52ek0x5uYAsusADooYT4ZQ2j8ch6W3-P-NyMWJndzgAxE_FapjCaoGHfPbCHB_fQ"
    # dps = get_department_list(token)

    wc = Wechat_Client()
    res = wc.get_department_list(wc.token)
    # wc.build_tree(res)
    # res = wc.get_dep_users(1, wc.token, 1)
    print(res)