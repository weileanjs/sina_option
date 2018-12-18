#coding:utf8
import datetime


def wait_seconds_step():
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    second = now.second
    start_second = 9*3600                                    # 爬虫起始运行时间（秒）
    stop_second = 15*3600                                     # 爬虫停止运行时间（秒）
    now_second = hour*3600 + minute*60 + second                 # 当日时间（秒）

    if now_second >= start_second and now_second <= stop_second:
        status = 1
        sleep_second = 300
    elif now_second < start_second:
        sleep_second = start_second - now_second
        status = 0
    else:
        sleep_second = 24*3600 - now_second + start_second
        status = 0
    print(status,sleep_second,now_second)
    return status,sleep_second


