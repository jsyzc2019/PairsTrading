﻿# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 16:56:01 2022

@author: admin
"""

# 使用ts
import tushare as ts
import json
from dateutil.parser import parse

# 请根据自己的情况填写ts的token
#setting = json.load(open('C:\config\config.json'))
######################################### tuhsare自动延迟下载 ####################################################
# tuhsare自动延迟下载，防止频繁调取数据是报错
import time
import logging
import logging.handlers


class TuShare:
    """tushare服务接口自动重试封装类，能够在接口超时情况下自动等待1秒然后再次发起请求，
    无限次重试下去，直到返回结果或者达到最大重试次数。
    """

    def __init__(self, token, logger=None, max_retry=0):
        """构造函数，token：tushare的token；logger：日志对象，可以不传；
        max_retry：最大重试次数，默认为0意为无限重试，建议用10以上100以内。"""
        self.token = token
        if not logger:
            logger = logging.getLogger('TuShare')
            # CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
            logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s %(name)s %(pathname)s:%(lineno)d %(funcName)s %(levelname)s %(message)s'
            )
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
            logger.addHandler(handler)
        self.logger = logger
        self.max_retry = max_retry
        ts.set_token(token)
        self.pro = ts.pro_api()

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            i = 0
            while True:
                try:
                    if name == 'pro_bar':
                        m = getattr(ts, name, None)
                    else:
                        m = getattr(self.pro, name, None)
                    if m is None:
                        self.logger.error('Attribute %s does not exist.', name)
                        return None
                    else:
                        return m(*args, **kwargs)
                except (Exception):
                    if self.max_retry > 0 and i >= self.max_retry:
                        raise
                    self.logger.exception(
                        'TuShare exec %s failed, args:%s, kwargs:%s, try again.',
                        name, args, kwargs)
                    time.sleep(1)
                i += 1

        return wrapper


#my_pro = TuShare(setting['token'], max_retry=60)  # 初始化ts

################################################################################
######################################### 公用 ####################################################
# 绕过查询限制
def distributed_query(query_func_name,
                      symbol,
                      start_date,
                      end_date,
                      fields,
                      limit=3000):
    n_symbols = len(symbol.split(','))
    dates = query_trade_dates(start_date, end_date)
    n_days = len(dates)

    if n_symbols * n_days > limit:
        n = limit // n_symbols

        df_list = []
        i = 0
        pos1, pos2 = n * i, n * (i + 1) - 1

        while pos2 < n_days:
            df = query_func_name(
                ts_code=symbol,
                start_date=dates[pos1],
                end_date=dates[pos2],
                fields=fields)
            df_list.append(df)
            i += 1
            pos1, pos2 = n * i, n * (i + 1) - 1
        if pos1 < n_days:
            df = query_func_name(
                ts_code=symbol,
                start_date=dates[pos1],
                end_date=dates[-1],
                fields=fields)
            df_list.append(df)
        df = pd.concat(df_list, axis=0)
    else:
        df = query_func_name(
            ts_code=symbol,
            start_date=start_date,
            end_date=end_date,
            fields=fields)
    return df


# ts的日历需要处理一下才会返回成交日列表
## 减少ts调用 改用jq的数据....
#df = my_pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date)

def query_trade_dates(df:list,start_date: str, end_date: str) -> list:    
    dates = df.query('is_open==1')['cal_date'].values.tolist()
    return  dates
    #return get_trade_days(start_date, end_date).tolist()

