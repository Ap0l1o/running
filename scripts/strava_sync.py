#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json

from config import JSON_FILE, SQL_FILE # JSON_FILE和SQL_FILE 分别是JSON文件和数据库的名称
from generator import Generator


def run_strava_sync(client_id, client_secret, refresh_token):
    generator = Generator(SQL_FILE)
    generator.set_strava_config(client_id, client_secret, refresh_token) # 设置starve api参数
    # if you want to refresh data change False to True
    generator.sync(False) # 从strava中同步数据到本地的数据库中

    activities_list = generator.load() # 从数据库中加载activity并存到一个列表中
    # 将所有activity写到json文件
    with open(JSON_FILE, "w") as f:
        json.dump(activities_list, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("client_id", help="strava client id")
    parser.add_argument("client_secret", help="strava client secret")
    parser.add_argument("refresh_token", help="strava refresh token")
    options = parser.parse_args()
    run_strava_sync(options.client_id, options.client_secret, options.refresh_token)
    # run_strava_sync(64343, 57f0c05e207b9738a07920e51bdf1464df6a01d0, cdfbe138a1610cb086393aa437e0f90d9132a6c1)

# client id 64343
# client secret 57f0c05e207b9738a07920e51bdf1464df6a01d0
# code 5311de49d4a705d1b97a399676d49424fe68d061
# refresh token cdfbe138a1610cb086393aa437e0f90d9132a6c1

# 获取 refresh token
# curl -X POST https://www.strava.com/oauth/token \
# -F client_id=64343 \
# -F client_secret=57f0c05e207b9738a07920e51bdf1464df6a01d0 \
# -F code=5311de49d4a705d1b97a399676d49424fe68d061 \
# -F grant_type=authorization_code

# {"token_type":"Bearer","expires_at":1654714679,"expires_in":17072,"refresh_token":"cdfbe138a1610cb086393aa437e0f90d9132a6c1","access_token":"69530c9d3a3ce665e7b5df321eb3cf2cd95e544b","athlete":{"id":64194147,"username":null,"resource_state":2,"firstname":"星飞","lastname":"姚","bio":"一个矛盾复杂到极致的人。","city":"青岛","state":"山东","country":null,"sex":"M","premium":false,"summit":false,"created_at":"2020-07-19T13:27:43Z","updated_at":"2021-12-07T08:36:13Z","badge_type_id":0,"weight":57.0,"profile_medium":"https://lh3.googleusercontent.com/a-/AOh14Ggberz0hApTwbz2RuIqg39WlLGHIuJF05Mpf4MRng=s96-c","profile":"https://lh3.googleusercontent.com/a-/AOh14Ggberz0hApTwbz2RuIqg39WlLGHIuJF05Mpf4MRng=s96-c","friend":null,"follower":null}}%  