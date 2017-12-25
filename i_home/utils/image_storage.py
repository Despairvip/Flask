# -*- coding:utf-8 -*-

from qiniu import Auth, put_data

access_key = "1qHahE1m5raWhZPNtaWNsWGqXNsJT8fP2yiwEHEn"
secret_key = "gpsWAOZyrsAMsxQ50BSuP-cYMpDqUk5AdoEJrHd_"

bucket_name = "despair"


def storage_image(data):
    """进行文件上传的工具类"""
    if not data:
        return None

    q = Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    # 第二个参数：key，代表指定保存的文件名，如果不传的话，七牛会默认生成文件名
    ret, info = put_data(token, None, data)

    if info.status_code == 200:
        # 代表上传成功
        return ret.get("key")
    else:
        # 代表上传失败
        raise Exception("七牛上传文件失败")

if __name__ == '__main__':
    file_name = raw_input("请输入文件名：")
    with open(file_name, "rb") as f:
        storage_image(f.read())