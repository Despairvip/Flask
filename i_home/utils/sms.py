# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from i_home.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# ���ʺ�
accountSid = '8aaf07086010a0eb01602ec9e2110c56'

# ���ʺ�Token
accountToken = '1ebf8161d69b4196890e9fd3af723d55'

# Ӧ��Id
appId = '8aaf07086010a0eb01602ec9e26a0c5d'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com'

# ����˿�
serverPort = '8883'

# REST�汾��
softVersion = '2013-12-26'


# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
# @param $tempId ģ��Id
class CCP(object):
    """��װ���Ͷ��Žӿ�"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            # ���õ���
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)
        return cls._instance

    def send_template_sms(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        print result
        if result.get("statusCode") == "000000":
            return 1
        else:
            return 0


if __name__ == '__main__':
     CCP().send_template_sms("17683780773", ["55555", 10], "1")

