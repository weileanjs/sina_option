import requests
from Log_Info.error_output import error_deco
from ImpliedVolatility import impliedVolatility
from config import get_header,get_leftdays_header
import re ,json , time ,datetime
from to_redis import opition2redis
from WaitTime.wait_time import wait_seconds_step

class sina_Option_Quotation(object):

    # 获取sina期权url代码,调用parseSinaEtf50Page,获取期权交易信息
    # eg  exercise_date   2018年10月交割为：1810
    def opition_code(self,exercise_date):
        url = 'http://hq.sinajs.cn/list=OP_UP_510050{},OP_DOWN_510050{}'.format(exercise_date,exercise_date)
        req = requests.get(url,headers=get_header(),timeout = 5)
        exercise_dict = {}
        property_dict ={}
        # json_data = json.loads(req.text.split('(')[1].split(')')[0].strip())
        for row in req.text.strip().split('\n'):
            sina_opition_code = row.split('"')[1][:-1]
            remaindedays = self.left_days(exercise_date)
            # self.parseSinaEtf50Page(sina_opition_code,remaindedays)
            url = 'http://hq.sinajs.cn/list={}'.format(sina_opition_code)
            req_page = requests.get(url,headers=get_header(),timeout = 5)                              # 行情数据
            req_delta = requests.get(url.replace('OP','SO'),headers=get_header(),timeout = 5)          # 希腊字母数据
            for row in req_delta.text.strip().split('\n'):
                d00 = self.formatText_property(row,remaindedays)
                property_dict.update(d00)
            for row_page in req_page.text.strip().split('\n'):
                d0 = self.formatText(row_page,remaindedays)
                exercise_dict.update(d0)
        return self.combineDict(property_dict,exercise_dict)

    # # 获取ETF50合约月份s,调用opition_code获取sina期权url代码
    def contract_month(self,):
        opitionDict = {}
        url = 'http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getStockName?callback=johansen0357170387563644941539590746929&exchange=%E4%B8%8A%E4%BA%A4%E6%89%80&cate=50ETF'
        req = requests.get(url,headers=get_leftdays_header(),timeout = 5)
        json_data = json.loads(req.text.split('(')[1].split(')')[0].strip())
        contractMonths = json_data['result']['data']['contractMonth'][-4:]
        for contractMonth in contractMonths:
            format_contractMonth = '{}{}'.format(contractMonth[2:4],contractMonth[-2:])
            opition_month_dict = self.opition_code(format_contractMonth)
            opitionDict.update(opition_month_dict)
        return opitionDict

    # 当前合约剩余天数
    def left_days(self,exec_date):
        format_exec_date ='20{}-{}'.format(exec_date[:2],exec_date[2:])
        url = 'http://stock.finance.sina.com.cn/futures/api/openapi.php/StockOptionService.getRemainderDay?exchange=%E4%B8%8A%E4%BA%A4%E6%89%80&cate=50ETF&date={}'.format(format_exec_date)
        req = requests.get(url,headers=get_leftdays_header(),timeout = 5)
        json_data = json.loads(req.text)
        remainderDays = json_data['result']['data']['remainderDays']
        remainderDays = remainderDays if int(remainderDays) > 0 else 1
        return remainderDays

    # 计算隐含波动率
    def calcImpliedVol(self,s0,x,mktprice,days,opition):

        clac = impliedVolatility(s0,x,mktprice,days)
        if opition == 'call':
            ImpliedVol = clac.callRealizedVol()
        else:
            ImpliedVol = clac.putRealizedVol()
        return '%0.4f' %ImpliedVol if ImpliedVol != None else None

    # 获取时间价值
    def getTimeValue(self,livePrice,exercisePrice,q_live_price,choice):
        if '购' in choice and float(exercisePrice) <=  float(livePrice):
            return '%0.4f'% (float(q_live_price) - (float(livePrice) - float(exercisePrice)))
        elif '购' in choice and float(exercisePrice) >  float(livePrice):
            return float(q_live_price)
        elif '沽' in choice and float(exercisePrice) <=  float(livePrice):
            return '%0.4f'% float(q_live_price)
        elif '沽' in choice and float(exercisePrice) >  float(livePrice):
            return '%0.4f'% (float(q_live_price)+ float(exercisePrice) - float(livePrice))
        else:
            return None
    # 格式化传入的数据,获取行情数据
    def formatText(self,text,remaindedays):
        d1 = {}
        quotation_dict = {}
        _text = text.split('"')[1].split(',')
        # for i ,v in enumerate(_text):
        #     print(i,v)
        key = _text[37]
        quotation_dict['remainde_days'] = int(remaindedays)                 #剩余天数
        quotation_dict['exercise_price'] = '%0.4f'%float(_text[7])          #行权价
        quotation_dict['buy_quantity'] = int(_text[0])                      #call买量
        quotation_dict['buy_price'] = '%0.4f'%float(_text[1])               #call买价
        quotation_dict['q_live_price'] = '%0.4f'%float(_text[2])            #最新价
        quotation_dict['sell_price'] = '%0.4f'%float(_text[3])              #call卖价
        quotation_dict['sell_quantity'] = '%0.4f'%float(_text[4])           #call卖量
        quotation_dict['inventory'] = '%0.4f'%float(_text[5])               #持仓量
        quotation_dict['up_down'] = '%0.4f'%float(_text[6])                 #涨跌幅
        quotation_dict['date'] = _text[32][:10]                             #交易日期
        quotation_dict['high'] = '%0.4f'%float(_text[39])                   #最高价
        quotation_dict['low'] = '%0.4f'%float(_text[40])                    #最低价
        quotation_dict['amount'] = int(_text[41])                           #成交量
        live_price = '%0.4f'%float(self.etf50QuotationLive())
        quotation_dict['time_value'] = self.getTimeValue(live_price,quotation_dict['exercise_price'],quotation_dict['q_live_price'],key)

        # if '购' in key:
        #     imVol = self.calcImpliedVol(float(live_price),float(quotation_dict['exercise_price']),float(quotation_dict['sell_price']),int(quotation_dict['remainde_days']),'call')
        # else:
        #     imVol = self.calcImpliedVol(float(live_price),float(quotation_dict['exercise_price']),float(quotation_dict['sell_price']),int(quotation_dict['remainde_days']),'put')
        # quotation_dict['impliedVol'] = imVol
        d1[key] = quotation_dict
        return d1

    # 格式化传入的数据,获取希腊数据
    def formatText_property(self,text,remaindedays):
        d1 = {}
        property_dict = {}
        _text = text.split('"')[1].split(',')
        # for i ,v in enumerate(_text):
        #     print(i,v)
        key = _text[0]
        property_dict['delta'] = '%0.4f'%float(_text[5])
        property_dict['gamma'] = '%0.4f'%float(_text[6])
        property_dict['theta'] = '%0.4f'%float(_text[7])
        property_dict['Vega'] = '%0.4f'%float(_text[8])
        property_dict['VIX'] = '%0.4f'%float(_text[9])
        d1[key] = property_dict
        return d1

    # 合并行情、希腊数据
    def combineDict(self,d1,d2):
        combine = {}
        for k1,v1 in d1.items():
            for k2,v2 in d2.items():
                if k1 ==k2:
                    d3 = {}
                    d3.update(v1)
                    d3.update(v2)
                    d3['utime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    combine[k1] = d3
        return combine

    def parseSinaEtf50Page(self,url_code,remaindedays):
        url = 'http://hq.sinajs.cn/list={}'.format(url_code)
        req = requests.get(url,headers=get_header(),timeout = 5)
        for row in req.text.strip().split('\n'):
            self.formatText(row,remaindedays)

    def etf50QuotationLive(self,):
        # ETF50当前价格，交易价非净价（估算）
        etf50_quotation_live = 'http://hq.sinajs.cn/list=s_sh510050'
        req = requests.get(etf50_quotation_live,headers=get_header(),timeout = 5)
        _etf50_price = float(re.search('50ETF,(.*?),',req.text).group(1))
        etf50_price = '%0.3f'%_etf50_price
        return etf50_price

@error_deco
def getOptionInfo():
    foo = sina_Option_Quotation()
    toRedis = opition2redis()
    # print(foo.opition_code('1811'))  # 单月数据
    info = foo.contract_month()        # 所有月月数据
    for k ,v in info.items():
        key = k.replace('购','CALL').replace('沽','PUT').replace('月','M').replace('50ETF','')
        # print('{}:  {} {}'.format(key,v,v['remainde_days']))
        toRedis.insert_hash(key,v,v['remainde_days'])




if __name__ == '__main__':
    while 1:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('START SINA_OPTION CRAWLER TIME {}:'.format(now))
        getOptionInfo()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('STOP SINA_OPTION CRAWLER TIME {}:'.format(now))
        stauts , seconds = wait_seconds_step()
        print('SLEEP SECONDE:{}'.format(seconds))
        time.sleep(seconds)

