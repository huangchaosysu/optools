# @Time    : 18-9-12 上午10:34
# @Author  : Chao
# @File    : app.py
import json
from utils.ad import LDAP_Client
from utils.wechat import Wechat_Client
from utils.log import logger


def get_groups(client):
    ad_groups = {}  # ad上的group信息
    for i in client.search('ou=groups,ou=people,dc=huangchao,dc=com', '*'):
        ad_groups[i[0].lower()] = i[1]
    return ad_groups


def get_users(client):
    ad_users = {}
    for i in client.search('ou=people,dc=huangchao,dc=com', '*'):
        name = i[0].split(',')[0].split('=')[1]
        ad_users[name] = i
    return ad_users


def run(fix=True):
    adclient = LDAP_Client()
    wxclient = Wechat_Client()

    # 获取微信的组织结构
    res = wxclient.get_department_list(wxclient.token)
    corp = wxclient.build_tree(res)

    ad_users = get_users(adclient)  # ad上的user
    ad_groups = get_groups(adclient)  # ad上的组

    for k in corp.keys():
        # 验证ad组是否存在(某个部门是否存在对应的ad组)
        dn = wxclient.get_dn(corp, k)
        if dn.lower() in ad_groups:
            del ad_groups[dn.lower()]
        else:
            logger.info('用户组' + dn + '在ad中不存在')
            if fix:
                adclient.add_group(dn)

    # 确定用户是否存在
    users = wxclient.get_users(1, wxclient.token, recursive=1)
    for u in users:
        if 'email' not in u:
            logger.error('用户%s邮箱为空' % u['name'])
            continue
        cn = u['email'].split('@')[0]
        if cn in ad_users:
            del ad_users[cn]
        else:
            logger.info('用户' + u['name'] + '在ad中不存在')
            if fix:
                adclient.add_user('cn=%s,ou=people,dc=huangchao,dc=com' % cn, '1d9ncu_34k')

    # 处理ad端多余的用户和组
    for k in ad_groups.keys():
        logger.info('用户组 %s 只在AD中存在' % k)
        if fix:
            adclient.delete(k)

    for k in ad_users.keys():
        logger.info('用户 %s 只在AD中存在' % k)
        if fix:
            adclient.delete(ad_users[k][0])

    # 校正完了用户组信息，重新从ad拉数据
    ad_groups = get_groups(adclient)
    ad_users = get_users(adclient)

    fixes = {}

    # 检查用户是否存在于特定的部门
    users = wxclient.get_users(1, wxclient.token, recursive=1)
    for u in users:  # 循环每个用户的部门列表进行校对
        if 'email' not in u:
            logger.error('校对--用户%s邮箱为空' % u['name'])
            continue
        cn = u['email'].split('@')[0]
        for dep in u['department']:
            dep_dn = wxclient.get_dn(corp, dep)
            if 'member' in ad_groups[dep_dn.lower()] and ad_users[cn][0].encode() in ad_groups[dep_dn.lower()]['member']:
                ad_groups[dep_dn.lower()]['member'].remove(ad_users[cn][0].encode())
            else:
                if fix:
                    if dep_dn in fixes:
                        fixes[dep_dn].append(ad_users[cn][0])
                    else:
                        fixes[dep_dn] = [ad_users[cn][0], ]
    for k in fixes:
        adclient.add_user_2_group(k, fixes[k])

    for g in ad_groups:
        if 'member' in ad_groups[g] and len(ad_groups[g]['member']) > 0:
            for m in ad_groups[g]['member']:
                logger.error('组 %s 存在非法的用户: %s' % (g, m))
                if fix:
                    adclient.delete_user_from_group(g, m)


if __name__ == "__main__":
    run()






