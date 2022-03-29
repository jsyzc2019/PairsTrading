#pip install git+https://github.com/JoinQuant/jqdatasdk.git -i https://mirrors.aliyun.com/pypi/simple/


import datetime
import numpy as np
import pandas as pd
import empyrical as ep # 收益分析基础计算

# 时间处理
import calendar
import empyrical as ep # 风险指标计算
from alphalens.utils import print_table
from dateutil.parser import parse

import itertools # 迭代器
import collections # 容器

from tqdm import tqdm_notebook # 进度条

#from jqdata import *
from jqdatasdk import *
from jqdatasdk import *auth('账号','密码')
jqdatasdk.auth('*****','')
# 画图
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # 导入设置坐标轴的模块

import sys 
sys.path.append("C://Users//huangtuo//Documents//GitHub//PairsTrading//new_stategy//Quantitative-analysis//") 
import foundation_tushare 
import json
# 请根据自己的情况填写ts的token
setting = json.load(open('C:\config\config.json'))
my_pro = foundation_tushare.TuShare(setting['token'], max_retry=60)

plt.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题
plt.style.use('seaborn')


def distributed_query(query_func_name, start: str, end: str, limit=3000, **kwargs) -> pd.DataFrame:
    '''用于绕过最大条数限制'''

    days = get_trade_days(start, end)
    n_days = len(days)

    if len(days) > limit:

        n = n_days // limit

        df_list = []

        i = 0

        pos1, pos2 = n * i, n * (i + 1) - 1

        while pos2 < n_days:

            df = query_func_name(
                start=dates[pos1],
                end=dates[pos2],
                **kwargs)

            df_list.append(df)

            i += 1

            pos1, pos2 = n * i, n * (i + 1) - 1

            if pos1 < n_days:

                df = query_func_name(
                    start=dates[pos1],
                    end=dates[-1],
                    **kwargs)

                df_list.append(df)

            df = pd.concat(df_list, axis=0)

    else:

        df = query_func_name(
            start=start, end=end, **kwargs)

    return df


def query_northmoney(start: str, end: str, fields: list) -> pd.DataFrame:
    '''北向资金成交查询'''

    select_type = ['沪股通', '深股通']

    select_fields = ','.join([f"finance.STK_ML_QUOTA.%s" % i for i in fields])

    q = query(select_fields).filter(finance.STK_ML_QUOTA.day >= start,
                                    finance.STK_ML_QUOTA.day <= end,
                                    finance.STK_ML_QUOTA.link_name.in_(select_type))

    return finance.run_query(q)


def query_north_hold(start: str, end: str, fields: list) -> pd.DataFrame:
    
    '''北向持股数据查询 2017年3月17号开始至今'''

    select_type = ['沪股通', '深股通']

    select_fields = ','.join(
        [f"finance.STK_HK_HOLD_INFO.%s" % i for i in fields])

    periods = get_trade_days(start, end)

    df_list = []

    for d in tqdm_notebook(periods, desc='查询北向持股数据'):
        
        for n in select_type:
            # 构造查询
            q = query(select_fields).filter(finance.STK_HK_HOLD_INFO.link_name == n,
                                            finance.STK_HK_HOLD_INFO.day == d)

            df_list.append(finance.run_query(q))

    return pd.concat(df_list)


def is_index_cons(df: pd.DataFrame, index_symbol: list) -> pd.DataFrame:
    '''
    判断是否为指数成分股并标记
    ---------
    df 列名必须包含 |day|code|
        day类型为datetime.date
    '''

    start = min(df['day']).year
    end = max(df['day']).year

    year_list = range(start, end + 1)

    dic_list = []  # 储存调仓日

    d = collections.defaultdict(list)

    # 获取每个调仓日节点
    for y, m in itertools.product(year_list, (6, 12)):

        change_day = OffsetDate(find_change_day(y, m, 'Friday', '2nd'), 1)
        def index_name(x): return get_security_info(x).name
        dic_list += [[(code, index_name(index_code)) for code in get_index_stocks(index_code, date=change_day)]
                     for index_code in index_symbol]

    temp_list = []
    for i in dic_list:
        temp_list += i

    for k, v in temp_list:

        d[k].append(v)

    df['is_cons'] = df['code'].apply(
        lambda x: ",".join(set(d.get(x, ['OTHER']))))

    return df


# 判断某年某月的第N个周几的日期
# 比如 2019，6月的第2个周五是几号
# 中证指数基本上都是每年6\12月第二个周五的下个交易日
def find_change_day(year, month, weekday, spec_weekday):
    '''
    find_day(y, 12, "Friday", "2nd")
    ================
    return datetime.date
        y年12月第二个周五
    '''
    DAY_NAMES = [day for day in calendar.day_name]
    day_index = DAY_NAMES.index(weekday)
    possible_dates = [
        week[day_index]
        for week in calendar.monthcalendar(year, month)
        if week[day_index]]  # remove zeroes

    if spec_weekday == 'teenth':

        for day_num in possible_dates:
            if 13 <= day_num <= 19:
                return datetime.date(year, month, day_num)

    elif spec_weekday == 'last':
        day_index = -1
    elif spec_weekday == 'first':
        day_index = 0
    else:
        day_index = int(spec_weekday[0]) - 1
    return datetime.date(year, month, possible_dates[day_index])


# 基于基准日偏移
def OffsetDate(end_date: str, count: int) -> datetime.date:
    '''
    end_date:为基准日期
    count:为正则后推，负为前推
    -----------
    return datetime.date
    '''

    trade_date = get_trade_days(end_date=end_date, count=1)[0]
    if count > 0:
        # 将end_date转为交易日

        trade_cal = get_all_trade_days().tolist()

        trade_idx = trade_cal.index(trade_date)

        return trade_cal[trade_idx + count]

    elif count < 0:

        return get_trade_days(end_date=trade_date, count=abs(count))[0]

    else:

        raise ValueError('别闹！')
        



def get_strategy_risk(algorithm_ret) -> pd.Series:

    ser = pd.Series({'年化收益率': ep.annual_return(algorithm_ret),
                     '年化波动率': ep.annual_volatility(algorithm_ret),
                     '最大回撤': ep.max_drawdown(algorithm_ret),
                     'Sharpe': ep.sharpe_ratio(algorithm_ret),
                     '收益回撤比': ep.calmar_ratio(algorithm_ret)})

    ser.name = '风险指标'

    return ser
    
    
daily_northmoney=my_pro.moneyflow_hsgt(start_date='20180125', end_date='20180808')