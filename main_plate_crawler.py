# coding=utf-8
from ths_plate.ths_gn_plates import get_ths_gn_plate
from ths_plate.ths_plates import get_ths_plates
import time, datetime
from config import GN_INFO,THSHY_INFO,DY_INFO
from ths_plate.ths_plate_stocks import plate_stocks_crawler
from see_szse.see_index_stocks import see_index_stocks_crawler
from see_szse.szse_index_stocks import  szse_index_stocks_crawler
from WaitTime.wait_time import wait_seconds
from multiprocessing import Process
import multiprocessing
# from kill import kill_firefox_geckodriver
# import io
# import sys
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')


"""
mark_id: 00: sz, 01:sh,02:hk
sec_type: 股票	01,债券	02,基金	03,权证	04,指数	05, 板块 20,题材	21,股指期货	06
"""



def ths_plate_run():
    '''
    爬取同花顺板块抓取
    :return:
    '''
    get_ths_plates(THSHY_INFO)
    get_ths_plates(DY_INFO)
    get_ths_gn_plate(GN_INFO)


def see_szse_run():
    '''
    爬取上、深交所指数及成分股
    :return:
    '''
    szse_index_stocks_crawler()
    see_index_stocks_crawler()


def plate_stock_js():
    '''
    同花顺板块成分股抓取
    :return:
    '''
    p1 = multiprocessing.Process(name='plate_stocks_crawler', target=plate_stocks_crawler)
    p1.deamon = True
    p1.start()
    p1.join(7000)
    print('d.is_alive()', p1.is_alive())
    p1.terminate()
    p1.join()
    print('d.is_alive()', p1.is_alive())






if __name__ == '__main__':
    while 1:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('START PLATES_CRAWLER  TIME :{}'.format(now))
        p1 = multiprocessing.Process(name='see_szse_run', target=see_szse_run)             # 交易所指数 包含个股
        p2 = multiprocessing.Process(name='ths_plate_run', target=ths_plate_run)           # 同花顺板块代码
        p3 = multiprocessing.Process(name='plate_stock_js', target=plate_stock_js)         # 同花顺板块成分股
        p1.deamon = True
        p2.deamon = True
        p3.deamon = True
        p1.start()
        p2.start()
        p3.start()
        p1.join(7200)
        p2.join(7200)
        p3.join(7200)
        p1.terminate()
        p2.terminate()
        p3.terminate()
        p1.join()
        p2.join()
        p3.join()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        seconde = wait_seconds()
        time.sleep(seconde)
        print('STOPPLATES_CRAWLER  TIME  :{}'.format(now))
