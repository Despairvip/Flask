# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from i_home.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# 主帐号
accountSid = '8aaf07086010a0eb01602ec9e2110c56'

# 主帐号Token
accountToken = '1ebf8161d69b4196890e9fd3af723d55'

# 应用Id
appId = '8aaf07086010a0eb01602ec9e26a0c5d'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id
class CCP(object):
    """封装发送短信接口"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            # 设置单例
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

