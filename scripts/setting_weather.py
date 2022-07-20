#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import stravalib
import requests
import argparse
import datetime
import json


def get_icon(icon) :
    new_icon = '🏃 🇨🇳 '
    if icon == "晴" :
        new_icon += '☀️'
    elif icon == "阴" :
        new_icon += '☁️'
    elif icon =="多云":
        new_icon += '☁️'
    elif icon == "少云":
        new_icon += '🌤️'
    elif icon == "晴间多云":
        new_icon += '⛅️'
    elif icon == "阵雨":
        new_icon += '🌦️'
    elif icon == "雷阵雨":
        new_icon += '⛈️'
    elif icon == "小雨":
        new_icon += '🌦️'
    elif icon == "中雨":
        new_icon += '🌧️'
    elif icon == "大雨":
        new_icon += '🌧️'
    elif icon == "小雪":
        new_icon += '🌨️'
    elif icon == "中雪":
        new_icon += '❄️'
    elif icon == "大雪":
        new_icon += '❄️'
    elif icon == "新月":
        new_icon += '🌑'
    elif icon == "蛾眉月":
        new_icon += '🌙'
    elif icon == "上弦月":
        new_icon += '🌓'
    elif icon == "盈凸月":
        new_icon += '🌔'
    elif icon == "满月":
        new_icon += '🌕'
    elif icon == "亏凸月":
        new_icon += '🌖'
    elif icon == "下弦月":
        new_icon += '🌗'
    elif icon == "残月":
        new_icon += '🌘'
    elif icon == "雾":
        new_icon += '🌫️'
        
    return new_icon
        
        


# 64343 57f0c05e207b9738a07920e51bdf1464df6a01d0 cdfbe138a1610cb086393aa437e0f90d9132a6c1
if __name__ == "__main__" :
    # 解析传递的参数
    parser = argparse.ArgumentParser()
    parser.add_argument("client_id", help="strava client id")
    parser.add_argument("client_secret", help="strava client secret")
    parser.add_argument("refresh_token", help="strava refresh token")
    options = parser.parse_args()
    
    # 构建Strava客户端
    strava_client = stravalib.Client()
    res = strava_client.refresh_access_token(
            client_id = options.client_id,
            client_secret = options.client_secret,
            refresh_token = options.refresh_token
        )
    strava_client.access_token = res['access_token']
    
    # 构造获取天气信息的参数
    weather_key = '750460f86bf045dfb8cf3f14d7272625'
    url = 'https://devapi.qweather.com/v7/weather/now?'
    params = {
        'location':'',
        'key': weather_key
    }   
    
    # 获取最新的datetime
    now_time = datetime.datetime.utcnow()
    for activity in strava_client.get_activities(before=now_time, limit=1):
        # 通过get_activities获得的activity信息不全，不过可以通过此函数获得activity id
        # 然后根据此id用get_activity函数获得完全信息的activity
        activity = strava_client.get_activity(activity.id)
        description = activity.description
        if description == None :
            description = ''
        # 如果以国旗开头，则表示已经设置好了
        if description.startswith('🇨🇳'):
            break
        
        # 获取天气信息
        location = activity.start_latlng
        lon = round(float(location.lon), 2)
        lat = round(float(location.lat), 2)
        params['location'] = str(lon) + "," + str(lat)
        weather_res = requests.get(url, params).text # 响应信息
        weather_info = json.loads(weather_res)['now'] # 从响应信息提取出天气信息
        text = weather_info['text'] # 文字描述
        icon = get_icon(text) # emoji
        temp = weather_info['temp'] # 温度
        feel_like = weather_info['feelsLike'] # 体感温度
        humidity = weather_info['humidity'] # 湿度
        wind_speed = weather_info['windSpeed'] # 风速
        wind_dir = weather_info['windDir'] # 风向
        
        weather_info = icon + " " + text + " , 气温 " + temp + "°C , 体感温度 " + feel_like + "°C , 相对湿度 " + humidity + "% , " + wind_dir + " " + wind_speed + "km/h \n" 
        
        new_description = weather_info + description
        new_name = icon + " " + activity.name
        
        res = strava_client.update_activity(activity.id, description = new_description, name = new_name)
        