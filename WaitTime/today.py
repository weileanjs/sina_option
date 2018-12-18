import time
def today():
    t =  time.time()
    #格式化时间戳为标准格式
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    # print(today)
    return today
