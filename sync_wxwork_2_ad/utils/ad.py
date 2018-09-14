# @Time    : 18-9-12 上午10:44
# @Author  : Chao
# @File    : ad.py
import ldap
import sys
import time
import json
from utils.log import logger


class LDAP_Client:
    def __init__(self):
        self.cli = ldap.initialize('ldap://172.16.60.108:389', bytes_mode=False)
        # self.cli = ldap.initialize('ldaps://172.16.60.108:636', bytes_mode=False)
        self.cli.protocol_version = 3
        # cli.set_option(ldap.OPT_REFERRALS, 0)
        # cli.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        # cli.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
        try:
            ret = self.cli.simple_bind('administrator@huangchao.com', 'Abcd1234')
            # ret = cli.simple_bind_s('administrator@abc.com', 'Abcd1234')
            # if ret[0] != 97:
            #     print('帐号认真失败')
            #     sys.exit(1)
            time.sleep(1)
        except Exception as e:
            logger.error(str(e))
            sys.exit(1)

    def __del__(self):
        try:
            self.cli.unbind()
        except:
            pass

    def add_group(self, base_dn):
        """
        base_dn: cn=test, ou=magicstack,dc=test,dc=com  NOT NONE
        """
        dn_list = base_dn.split(',')
        user_info = dict()
        for item in dn_list:
            attr, value = item.split('=')
            user_info[attr] = value
        add_record = [('objectclass', [b'top', b'group']),
                      ('cn', [('%s' % user_info.get("cn")).encode(), ]),
                      ]
        try:
            result = self.cli.add_s(base_dn, add_record)
        except Exception as e:
            logger.error('添加组失败:' + str(e))
            return False
        else:
            if result[0] == 105:
                return True
            else:
                logger.error('添加组失败: ' + json.dumps(result))
                return False

    def add_department(self, base_dn):
        """
        base_dn: cn=test, ou=magicstack,dc=test,dc=com  NOT NONE
        """
        dn_list = base_dn.split(',')
        user_info = dict()
        for item in dn_list:
            attr, value = item.split('=')
            user_info[attr] = value
        add_record = [('objectclass', [b'top', b'organizationalUnit']),]
        try:
            result = self.cli.add_s(base_dn, add_record)
        except Exception as e:
            logger.error('添加部门失败: ' + str(e))
            return False
        else:
            if result[0] == 105:
                return True
            else:
                logger.error('添加部门失败: ' + json.dumps(result))
                return False

    def add_user(self, base_dn, password):
        """
        base_dn: ou=magicstack,dc=test,dc=com  NOT NONE
        """
        logger.info('添加AD用户' + base_dn)
        dn_list = base_dn.split(',')
        user_info = dict()
        for item in dn_list:
            attr, value = item.split('=')
            user_info[attr] = value
        add_record = [('objectclass', [b'top', b'user', b'person', b'organizationalperson']),
                      ('cn', [('%s' % user_info.get("cn")).encode(), ]),
                      ('sn', [('%s' % user_info.get("cn")).encode(), ]),
                      ('userpassword', [('%s' % password).encode()], )]
        try:
            result = self.cli.add_s(base_dn, add_record)
        except Exception as e:
            logger.error('添加用户失败: ' + str(e))
            return False
        else:
            if result[0] == 105:
                return True
            else:
                logger.error('添加用户失败: ' + json.dumps(result))
                return False

    def delete(self, dn):
        try:
            result = self.cli.delete_s(dn)
        except Exception as e:
            logger.error('删除' + dn + '失败:' + str(e))
            return False
        else:
            if result[0] == ldap.RES_DELETE:
                return True
            else:
                logger.error('删除用户失败: %s, %s' % (dn, json.dumps(result)))
                return False

    def exists(self, dn):
        try:
            res = self.cli.search_s(dn, ldap.SCOPE_BASE)
            if res:
                return True
            else:
                return False
        except ldap.NO_SUCH_OBJECT:
            return False


    def search(self, base_dn, cn):
        try:
            res = self.cli.search_s(base_dn, ldap.SCOPE_ONELEVEL, '(cn=%s)' % cn)
            return res
        except:
            return []

    def add_user_2_group(self, group_dn, user_dns):
        try:
            logger.info("把用户添加到组: %s, %s" % (group_dn, json.dumps(user_dns)))
            res = self.cli.modify_s(group_dn, [(ldap.MOD_ADD, 'member', udn.encode()) for udn in user_dns])
            if res[0] == ldap.RES_MODIFY:
                return True
            else:
                logger.error('把用户添加到组失败:' + json.dumps(res))
                return False
        except Exception as e:
            logger.error('把用户添加到组失败:' + str(e))

    def delete_user_from_group(self, group_dn, user_dn):
        try:
            logger.info("从组删除用户: %s, %s" % (group_dn, str(user_dn)))
            res = self.cli.modify_s(group_dn, [(ldap.MOD_DELETE, 'member', user_dn)])
            if res[0] == ldap.RES_MODIFY:
                return True
            else:
                logger.error('从组删除用户:' + json.dumps(res))
                return False
        except Exception as e:
            logger.error('从组删除用户:' + str(e))

if __name__ == "__main__":
    cli = LDAP_Client()
    # print(cli.exists('cn=tgroup,ou=groups,ou=people,dc=huangchao,dc=com'))
    # res = cli.cli.search_s('cn=黄超的公司-广州研发,ou=groups,ou=people,dc=huangchao,dc=com', ldap.SCOPE_SUBTREE)
    res = cli.cli.modify_s('cn=黄超的公司-财务部,ou=groups,ou=people,dc=huangchao,dc=com', [(ldap.MOD_DELETE, 'member', b'cn=huangchao,ou=people,dc=huangchao,dc=com')])
    print(res)
    # cli.exists('ou=HUANGCHAO1,dc=huangchao,dc=com')
    # cli.add_group('cn=default,ou=HUANGCHAO,dc=huangchao,dc=com')
